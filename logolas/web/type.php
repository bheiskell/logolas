<?php
error_reporting(E_ALL);

header('Content-type: application/json');

$mysqli = new mysqli("localhost", "logger-web", "", "logger");

if (mysqli_connect_errno()) { exit(); }

echo json_encode(columns($mysqli));

$mysqli->close();

/**
 * Get all columns
 */
function columns($mysqli) {
	$columns = array();
	$result = $mysqli->query("
		SELECT DISTINCT column_name
		FROM information_schema.columns
		WHERE table_schema = 'logger'
		ORDER BY column_name;
	");

	while ($row = $result->fetch_array(MYSQLI_ASSOC)) {
		$columns[] = $row['column_name'];
	}
	return $columns;
}
