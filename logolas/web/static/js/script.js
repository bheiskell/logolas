$().ready(function() {

	var container = $('#logs');

	var last_time = yesterdays_date();

	var poll = true;

	var view = {
		/**
		 * Track the number of filters created for manual form indexing
		 */
		filter_count: 0,

		/**
		 * Valid column types
		 */
		columns: [ 'time' ],

		/**
		 * Initialize the view
		 */
		initialize: function() {
			$('fieldset:first').append(this.get_default_filter());

			$('#filter h2')
				.css({ 'cursor': 'pointer' })
				.data('width', $('#filter').innerWidth())
				.toggle(
					function() {
						$(this)
							.parent()
							.animate({ width: 50 })
							.children(':not(h2)')
							.hide();
					},
					function() {
						$(this)
							.parent()
							.css({ width: $(this).data('width') })
							.children()
							.show();
					}
				)
				.trigger('click');

			$('<button>reset</button>')
				.insertAfter('fieldset:first')
				.click(function(e) {
					e.preventDefault();
					$('fieldset:first').empty();
					view.get_default_filter();
				});

			$('<button>add</button>')
				.insertAfter('fieldset:first')
				.click(function(e) {
					e.preventDefault();
					$('fieldset:first').append(
						view.get_filter_template('['+view.filter_count+']')
					);
				});

			$('<button>filter</button>')
				.insertAfter('fieldset:first')
				.click(function(e) {
					e.preventDefault();
					view.purge();
					poll = false;
					controller($('form:first').serialize());
				});
		},

		/**
		 * Purge all handled messages
		 */
		purge: function() {
			container.empty();
		},

		/**
		 * Handle updates to the view
		 */
		update: function(messages) {
			at_bottom = (window.pageYOffset >= window.scrollMaxY);

			for (i in messages) {
				var message = messages[i];

				if ($('#' + message.hash).length) { continue; }

				var ol = $('<ol/>').addClass(message.type).attr('id', message.hash);

				ol.append($('<li/>').text(message.time).addClass('time'));
				ol.append($('<li/>').text(message.type).addClass('type'));

				for (key in message.data) {
					ol.append($('<li/>').text(message.data[key]).addClass(key));
				}

				container.append(ol);

				last_time = message.time;
			}

			if (at_bottom) window.scrollTo(0, document.body.scrollHeight);
		},

		/**
		 * Get default filter
		 */
		get_default_filter: function() {
			return this
				.get_filter_template('[0]')
				.children('[name*=column]').val('time').trigger('change')
				.nextAll('input').val(last_time)
				.parent();
		},

		/**
		 * Get template of filter form elements
		 */
		get_filter_template: function(realized_index) {
			view.filter_count++;

			var foundation = {
				'conditional': [ 'AND', 'OR' ],
				'column':      this.columns,
				'operator':    [ '>=', '<=', '=', 'LIKE' ],
				'filter':      '',
			};

			var result = $('<fieldset/>');

			for (field_type in foundation) {
				var values = foundation[field_type];
				var element = $('<input/>')

				if (values instanceof Array) {
					element = $('<select/>');

					for (i in values) {
						$('<option/>')
							.text(values[i].toLowerCase())
							.attr('value', values[i])
							.appendTo(element);
					}
				}

				element.attr('name', 'filters' + realized_index + '[' + field_type + ']');

				// The time column warrants a special formatting on the input
				if ('column' == field_type) {
					element.change(function() {
						('time' == $(this).val())
							? $(this).nextAll('input').mask('9999-99-99 99:99:99')
							: $(this).nextAll('input').unmask();
					});
				}

				element.appendTo(result);
			}

			$('<button/>')
				.text('remove')
				.appendTo(result)
				.click(function() {
					$(this).closest('fieldset').remove();
				});

			return result;
		},
		set_columns: function(columns) {
			view.columns = columns;
		},
	};

	function controller(filters) {
		$.ajax({
			type: 'GET',
			url: 'poll.php',
			dataType: 'json',
			data: filters,
			success: view.update,
		});

		if (filters['filters'][0]['column'] == 'time') {
			filters['filters'][0]['filter'] = last_time;
		}
		if (poll) { setTimeout(function() { controller(filters) }, 5000); }
	}

	/**
	 * Get yesterday's date
	 */
	function yesterdays_date() {
		var pad = function (string, number, character) {
			if (isNaN(number)) return null;

			character = character || '0';

			string = String(string);

			var pad = new Array(number)
					.join(character)
					.substring(0, number-string.length);
			return pad + string;
		};

		var date = new Date();
		date.setDate(date.getDate() - 1);

		var result =    pad(date.getFullYear(),  4)
			+ '-' + pad(date.getMonth() + 1, 2)
			+ '-' + pad(date.getDate(),      2)
			+ ' ' + pad(date.getHours(),     2)
			+ ':' + pad(date.getMinutes(),   2)
			+ ':' + pad(date.getSeconds(),   2);

		return result;
	}

	$.ajax({
		type: 'GET',
		url: 'type.php',
		dataType: 'json',
		success: view.set_columns,
		async: false,
	});

	view.initialize();

	controller({
		'filters': [
			{
				'column': 'time',
				'operator': '>=',
				'conditional': 'AND',
				'filter': last_time,
			},
		],
		'limit': 100,
	});
});
