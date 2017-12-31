/**
 * MIT License
 *
 * Copyright (c) 2017 Nils Homer
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 **/

/**
 * Note: some of this code was derived from:
 *   https://github.com/piotros/json-path-picker
 * The original LICENSE is included below.
 *
 * MIT License
 *
 * Copyright (c) 2016 Piotr Baran
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 **/

(function ($) {
	var $pathTarget = $('.json-output');
	var isUrlRegex = /^(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/
	var santizeIdRegex = /[^A-Za-z0-9\-_:\.]+/g
	var santizeIdEnforceLeadingAlpha = /^[^A-Za-z]+/g

	/**
	 * Check if arg is either an array with at least 1 element, or a dict with at least 1 key
	 * @return boolean
	 */
	function isCollapsable(arg) {
		return arg instanceof Object && Object.keys(arg).length > 0;
	}

	/**
	 * Check if a string represents a valid url
	 * @return boolean
	 */
	function isUrl(string) {
		return isUrlRegex.test(string);
	}

	function sanitizeId(string) {
		return string.replace(santizeIdRegex, '').replace(santizeIdEnforceLeadingAlpha, '');
	}

	/**
	 * Transform a json object into html representation
	 * @return string
	 */
	function jsonMetricDefs2Html(json, keyIdPrefix) {
		// FIXME: add in a "select all" list item...

		var html = '';
		if (typeof json === 'string' ||
			typeof json === 'number' ||
			typeof json === 'boolean' ||
			json === null ||
			json instanceof Array) {
			// do nothing, print nothing
		}
		else if (typeof json === 'object') {
			var key_count = Object.keys(json).length;
			var firstKey = null;
			for (var key in json) {
				if (json.hasOwnProperty(key)) {
					firstKey = key;
					break;
				}
			}
			if (key_count == 0 || (key_count == 1 && firstKey == "None")) {
				// go directly to the child
				var keyReprId = sanitizeId(firstKey);
				if (keyIdPrefix.length > 0) {
					keyReprId = keyIdPrefix + "-" + keyReprId
				}
				html += jsonMetricDefs2Html(json[key], keyReprId);
			}
			else {
				html += '<ul class="json-dict">';
				for (var key in json) {
					if (json.hasOwnProperty(key)) {
						html += '<li data-key-type="object" data-key="' + key + '">';
						var keyRepr = key
						var keyReprId = sanitizeId(keyRepr);
						if (keyIdPrefix.length > 0) {
							keyReprId = keyIdPrefix + "-" + keyReprId
						}
							
						var childHtml = jsonMetricDefs2Html(json[key], keyReprId);

						// Add toggle button if item is collapsible
						if (isCollapsable(json[key])) {
							html += '<a href class="json-toggle">' + keyRepr + '</a>';
						}
						else {
							if (childHtml.length == 0) {
								html += '<label><input type="checkbox" class="pick-metric single-metric" title="Pick metric" name="' + keyReprId + '">' + keyRepr + '</label>';
								//html += '<input type="checkbox" class="pick-metric" title="Pick metric" name="' + keyReprId + '">';
							}
							else {
								html += keyRepr;
							}
						}
						html += childHtml
						html += '</li>';
					}
				}
				html += '</ul>';
			}
		}
		return html;
	}
	
	/**
	 * jQuery plugin method
	 */
	$.fn.jsonMetricDefs = function (json) {

		// jQuery chaining
		return this.each(function () {
			// Transform to HTML
			var html = jsonMetricDefs2Html(json, "")

			// Insert HTML in target DOM element
			$(this).html(html);

			// Bind click on toggle buttons
			$(this).off('click');
			$(this).on('click', 'a.json-toggle', function () {
				var target = $(this).toggleClass('collapsed').siblings('ul.json-dict, ol.json-array');
				target.toggle();
				if (target.is(':visible')) {
					target.siblings('.json-placeholder').remove();
				}
				else {
					var count = target.children('li').length;
					var placeholder = count + (count > 1 ? ' items' : ' item');
					target.after('<a href class="json-placeholder">' + placeholder + '</a>');
				}
				return false;
			});

			// Simulate click on toggle button when placeholder is clicked
			$(this).on('click', 'a.json-placeholder', function () {
				$(this).siblings('a.json-toggle').click();
				return false;
			});

			$(this).on('click', 'input.pick-metric', function () {
				if ($pathTarget.length === 0) {
					return;
				}

				var path = $(this).attr('name');

				// toggle the metrics row
				$("#json-metric-data-renderer table.metrics-table #" + path).toggle();
				var visible = $pathTarget.is(":visible");

				if (visible) {
					// explicitly show the remove button
					$('button.pick-metric').show();
					path = "Showing row: " + path;
				}
				else {
					path = "Hiding row: " + path;
				}

				$pathTarget.val(path);
			});

			// Trigger click to collapse all nodes
			$(this).find('a.json-toggle').click();
		});
	}
  
	function jsonMetricData2Html(json, sampleJson, keyIdPrefix) {
		var html = '';

		if (typeof sampleJson !== 'object') {
			return 'Error: Metric data was JSON but in the wrong format';
		}
		html += '<table class="metrics-table">';

		
		// header
		html += '<tr class="metric-table metric-row-header">';
		html += '<th class="metric-table metric-column-header metric-column-header-delete"></th>'; // for the delete button
		html += '<th class="metric-table metric-column-header metric-column-header-group">Group</th>';
		html += '<th class="metric-table metric-column-header metric-column-header-category">Category</th>';
		html += '<th class="metric-table metric-column-header metric-column-header-name">Name</th>';
		for (var sampleKey in json) {
			if (!json.hasOwnProperty(sampleKey)) {
				continue;
			}
			html += '<th class="metric-table metric-column-header metric-column-header-sample">' + sampleKey + '</th>';
		}
		html += '</tr>';

		// Go through each metric group
		var numGroups = 0;
		for (var groupKey in sampleJson) {
			if (!sampleJson.hasOwnProperty(groupKey)) {
				continue;
			}
			var groupJson = sampleJson[groupKey];
			if (typeof groupJson !== 'object') {
				return 'Error: Metric data was JSON but in the wrong format';
			}
			numGroups += 1;

			// Go through each metric category
			var numCategories = 0;
			for (var categoryKey in groupJson) {
				if (!groupJson.hasOwnProperty(categoryKey)) {
					continue;
				}
				var categoryJson = groupJson[categoryKey];
				if (typeof categoryJson !== 'object') {
					return 'Error: Metric data was JSON but in the wrong format';
				}
				numCategories += 1;

				// go through each metric
				var numMetrics = 0;
				for (var metricKey in categoryJson) {
					if (!categoryJson.hasOwnProperty(metricKey)) {
						continue;
					}
					numMetrics += 1;

					rowId = sanitizeId(groupKey + '-' + categoryKey + '-' + metricKey);

					html += '<tr class="metric-table metric-row" id="' + rowId + '">';
					html += '<td class="metric-table metric-column"><button type="button" style="display: block;" class="pick-metric" id="' + rowId + '">Remove</button></td>'; // FIXME: use an icon
					html += '<td class="metric-table metric-column metric-column-group">' + groupKey + '</td>';
					html += '<td class="metric-table metric-column metric-column-category">' + categoryKey + '</td>';
					html += '<td class="metric-table metric-column metric-column-name">' + metricKey + '</td>';

					// for every sample
					for (var sampleKey in json) {
						if (!json.hasOwnProperty(sampleKey)) {
							continue;
						}
						var sample = json[sampleKey];
						if (!sample.hasOwnProperty(groupKey)) {
							return 'Error: metric group "' + groupKey + '" missing from sample "' + sampleKey + '"';
						}
						var group = sample[groupKey];
						if (!group.hasOwnProperty(categoryKey)) {
							return 'Error: metric category "' + categoryKey +'" missing from group "' + groupKey + '" and sample "' + sampleKey + '"';
						}
						var category = group[categoryKey];
						if (!category.hasOwnProperty(metricKey)) {
							return 'Error: metric "' + metricKey + '" missing from category "' + categoryKey + '", group "' + groupKey + '", and sample "' + sampleKey + '"';
						}
						var metric = category[metricKey];

						// format it!!!
						html += '<td class="metric-table metric-column">'
						if (typeof metric === 'string') {
							// Escape tags
							metric = metric.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
							if (isUrl(metric))
								html += '<a href="' + metric + '" class="json-string">' + metric + '</a>';
							else
								html += '<span class="json-string">"' + metric + '"</span>';
						}
						else if (typeof metric === 'number') {
							html += '<span class="json-literal">' + metric + '</span>';
						}
						else if (typeof metric === 'boolean') {
							html += '<span class="json-literal">' + metric + '</span>';
						}
						else if (metric === null) {
							html += '<span class="json-literal">null</span>';
						}
						else {
							html += '<span class="json-mssing">JSON Value Not Supported</span>';
						}
						html += '</td>';
					}
					html += '</tr>';
				}
				if (numMetrics == 0) {
					return 'No metric data found in group "' + groupKey + '" and category "' + categoryKey + '"!';
				}
			}
			if (numCategories == 0) {
				return 'No metric data found in group "' + groupKey + '"!';
			}
		}
		if (numGroups == 0) {
			return 'No metric data found (no metric groups in the first sample)!';
		}
		html += '</table>';

		return html;
	}

	/**
	 * jQuery plugin method
	 */
	$.fn.jsonMetricData = function (json, sampleJson) {
		// jQuery chaining
		return this.each(function () {

			// Transform to HTML
			var html = jsonMetricData2Html(json, sampleJson, "")

			// Insert HTML in target DOM element
			$(this).html(html);
			
			$(this).on('click', 'button.pick-metric', function () {
				var path = this.id
				$("#json-metric-data-renderer table.metrics-table #" + path).hide();
				path = "Removing row: " + path;
				$pathTarget.val(path);
			});

			// hide all rows by default
			$("table.metrics-table tr.metric-row").hide();
		});
	}

    // Method that checks that the browser supports the HTML5 File API
	function browserSupportFileUpload() {
		var isCompatible = false;
		if (window.File && window.FileReader && window.FileList && window.Blob) {
			isCompatible = true;
		}
		return isCompatible;
	}
	
	function getSampleJson(json) {
		if (typeof json !== 'object') {
			alert('Error: Metric data was JSON but in the wrong format');
			return null;
		}

		// Just get the first sample's data, so we can get the group/category/name
		var sampleJson = null;
		for (var key in json) { 
			if (json.hasOwnProperty(key)) {
				sampleJson = json[key];
				break;
			}
		}
		if (sampleJson == null) {
			alert('No metric data found (no samples)!');
			return null;
		}
		if (typeof sampleJson !== 'object') {
			alert('Error: Metric data was JSON but in the wrong format');
			return null;
		}
		return sampleJson
	}
	
	$("#json-metric-data").change(function() {
		if (!browserSupportFileUpload()) {
			alert('The File APIs are not fully supported in this browser!');
		} else {
			var files = $("#json-metric-data").prop('files');
			var file = files[0];
			var reader = new FileReader();
			reader.readAsText(file);
			reader.onload = function(event) {
				var jsonMetricData = event.target.result;

				// Load in the JSON data
				try { 
					if (jsonMetricData.length == 0) return alert("No JSON data given.");
					var json = eval('(' + jsonMetricData + ')');
				}     
				catch (error) {
					return alert("Cannot eval JSON: " + error);
				}   

				// Get the JSON for the first sample
				sampleJson = getSampleJson(json);

				// Load the metric definitions from the first sample
				$('#json-metric-defs-renderer').jsonMetricDefs(sampleJson);

				// Load the metric data
				$('#json-metric-data-renderer').jsonMetricData(json, sampleJson);

				// Show the main div
				$('.content').css('display', 'inline-block');
			};
			reader.onerror = function() {
				alert('Unable to read ' + file.fileName);
			};
		}
	});

})(jQuery);
