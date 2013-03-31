<?php
error_reporting(E_ALL);

header('Content-type: application/json');

$mysqli  = connect();
$models  = models($mysqli);
$results = fetch( $mysqli, $models, $_GET['filters'], (int)$_GET['limit']);

echo json_encode($results);

$mysqli->close();

/**
 * Establish database connection
 */
function connect() {
	$mysqli = new mysqli("localhost", "logger-web", "", "logger");

	if (mysqli_connect_errno()) { die('[Error] DB Connection'); }

	return $mysqli;
}

/**
 * Pull database model definitions from the database
 */
function models($mysqli) {
	$tables = array();
	$result = $mysqli->query("
		SELECT table_name, GROUP_CONCAT(column_name) AS columns
		FROM information_schema.columns
		WHERE table_schema = 'logger'
		GROUP BY table_name
	");

	while ($row = $result->fetch_array(MYSQLI_ASSOC)) {
		$tables[$row['table_name']] = explode(',', $row['columns']);
	}
	return $tables;
}

/**
 * Obtain where clause from filter
 */
function where($mysqli, $filters, $columns) {
	$where = '';
	$applied_filters = 0;
	foreach ($filters as $filter) {
		if (numeric_keys($filter)) {
			$where .= ' AND (' . where($mysqli, $filter, $columns) . ')';

		} else {
			if (!in_array($filter['operator'],    array('=', '<=', '>=', 'LIKE'))
			 || !in_array($filter['conditional'], array('AND', 'OR'))
			) { die('[Error] Bad Filter'); }

			// First conditional must be ignored for valid SQL
			if (0 == $applied_filters) {
				$filter['conditional'] = '';
			}

			$where .= sprintf(
				" %s %s %s '%s'",
				$filter['conditional'],
				$filter['column'],
				$filter['operator'],
				$mysqli->real_escape_string($filter['filter'])
			);

			$applied_filters++;
		}
	}
	return $where;
}

/**
 * Fetch the logs
 */
function fetch($mysqli, $models, $filters, $limit) {
	$results = array();

	foreach ($models as $table => $columns) {
		if (filter_applicable($filters, $columns)) {

			$where = where($mysqli, $filters, $columns);
			$query = "
				SELECT * FROM {$table}
				WHERE {$where}
				ORDER BY time DESC
				LIMIT {$limit} 
			";

			if (!$result = $mysqli->query($query)) die('[Error] Bad Query'.$query);

			while ($row = $result->fetch_array(MYSQLI_ASSOC)) {
				$row['type'] = str_replace('_log', '', $table);
				$results[] = $row;
			}
			$result->close();
		}
	}


	usort($results, "date_sort");

	// Adapter post-processing
	foreach ($results as &$result) {
		foreach ($result as $key => $value) {
			if (!in_array($key, array('time', 'type', 'id', 'data'))) {
				$result['data'][$key] = $value;
				unset($result[$key]);
			}
		}
		$result['hash'] = $result['type'] . $result['id'];
	}

	// The limit applied to the queries is purely for a performance boost.
	// The actual limit occurs here by trimming from the end. If we were
	// just to rely on the query limit, we would get N*limit for N tables.
	// Also the older data would look confusing, because if one type of log
	// is more common, it would stop reporting at some point (because it
	// hit the limit) where as the other logs would still be displayed.
	return array_splice($results, sizeof($results) - $limit);
}

/**
 * Determine if the keys in this array are numeric
 */
function numeric_keys($array) {
	$numeric = true;
	foreach (array_keys($array) as $key) {
		if (!is_numeric($key)) {
			$numeric = false;
		}
	}
	return $numeric;
}

/**
 * Determine if a table is applicable to a filter.
 */
function filter_applicable($filters, $columns) {
	$result = true;
	foreach ($filters as $filter) {
		if ((numeric_keys($filter) && !filter_applicable($filter, $columns))
		 || (!in_array($filter['column'], $columns))
		) {
			$result = false;
		}
	}
	return $result;
}

/**
 * Array sort callback that sorts by the time key
 */
function date_sort($a, $b) {
	if ($a['time'] == $b['time']) return 0;
	return ($a['time'] < $b['time']) ? -1 : 1;
}
