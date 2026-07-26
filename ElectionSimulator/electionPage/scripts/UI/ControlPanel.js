/**
 * ControlPanel previews how the results will roll in (a seat projection chart + per-riding stats),
 * lets the moderator manually reorder which riding is featured on the Primary/Secondary panel at
 * each time slot, and lets them hand-edit or reroll a riding's individual polling steps - all
 * before the schedule is locked in and the live broadcast starts. This is what replaces the dead
 * "Control Panel" button/control.html that used to be here.
 */
class ControlPanel
{
	static #area = $("#controlPanel")
	static #chartCanvas = $("#seatProjectionChart")[0]
	static #primaryList = $("#primaryScheduleList")
	static #secondaryList = $("#secondaryScheduleList")
	static #reportingOrderList = $("#reportingOrderList")

	static #statsTable = $("#statsTable")
	static #statsMinStepInput = $("#statsMinStep")
	static #statsSortField = "closestMarginLate"
	static #statsSortAsc = true

	static #jumpList = $("#stepEditorJumpList")
	static #ridingLabel = $("#stepEditorRidingLabel")
	static #stepEditorTable = $("#stepEditorTable")
	static #stepEditorFrom = $("#stepEditorFrom")
	static #stepEditorTo = $("#stepEditorTo")
	static #stepChartCanvas = $("#stepChart")[0]

	static #parties
	static #ridings
	static #primaryDuration
	static #secondaryDuration
	static #schedule
	static #onConfirm
	static #selectedRiding = null

	/**
	 * show renders the control panel and wires up its buttons.
	 *
	 * @param {Object} parties key -> Party
	 * @param {Array} ridings array of Riding
	 * @param {float} primaryDuration
	 * @param {float} secondaryDuration
	 * @param {Function} onConfirm called with the finalized schedule once the moderator goes live
	 */
	static show(parties, ridings, primaryDuration, secondaryDuration, onConfirm)
	{
		ControlPanel.#parties = parties
		ControlPanel.#ridings = ridings
		ControlPanel.#primaryDuration = primaryDuration
		ControlPanel.#secondaryDuration = secondaryDuration
		ControlPanel.#onConfirm = onConfirm
		ControlPanel.#selectedRiding = ridings.length > 0 ? ridings[0] : null

		$("#setup").css("display", "none")
		ControlPanel.#area.css("display", "flex")

		ControlPanel.#reroll()

		// These are <input type="button"> (not <button>) on purpose: SetUp.js binds
		// $("button").click(...) to advance its own setup generator, and these controls must not
		// accidentally trigger that.
		$("#rerollScheduleBtn").off("click").on("click", ControlPanel.#reroll)
		$("#rerollReportingOrderBtn").off("click").on("click", ControlPanel.#rerollReportingOrder)
		$("#confirmScheduleBtn").off("click").on("click", ControlPanel.#confirm)
		$("#compileVideoBtn").off("click").on("click", ControlPanel.#compileVideo)
		$("#stepEditorRerollRangeBtn").off("click").on("click", ControlPanel.#rerollSelectedRange)
		$("#stepEditorRerollAllBtn").off("click").on("click", ControlPanel.#rerollAllSteps)
		$("#rerollAllRidingsBtn").off("click").on("click", ControlPanel.#rerollAllRidings)
		ControlPanel.#statsMinStepInput.off("change").on("change", ControlPanel.#drawStatsTable)

		ControlPanel.#drawReportingOrder()
		ControlPanel.#drawJumpList()
		ControlPanel.#drawStepEditor()
		ControlPanel.#drawStatsTable()
		ControlPanel.#ridingLabel.text(ControlPanel.#selectedRiding !== null ? ControlPanel.#selectedRiding.getName() : "No riding selected")
	}

	/**
	 * #reroll generates a fresh random display schedule (which riding the Primary/Secondary panel
	 * shows at a given moment) and redraws the chart + running-order lists. This does NOT change
	 * when any riding's results are actually decided - see #rerollReportingOrder for that - so the
	 * Seat Projection chart is unaffected by it.
	 */
	static #reroll()
	{
		ControlPanel.#schedule = Scheduler.build
		(
			ControlPanel.#ridings,
			Scheduler.PRIMARY_POOL_MAX,
			Scheduler.SECONDARY_POOL_MAX,
			ControlPanel.#primaryDuration,
			ControlPanel.#secondaryDuration
		)

		ControlPanel.#drawChart()
		ControlPanel.#drawList(ControlPanel.#primaryList, ControlPanel.#schedule.primary)
		ControlPanel.#drawList(ControlPanel.#secondaryList, ControlPanel.#schedule.secondary)
	}

	/**
	 * #ridingsSortedByStartTime returns every riding sorted by its current start time - the
	 * "Reporting Order" is just this list, re-derived fresh every draw (there's no separate stored
	 * order - a riding's start time IS its position).
	 *
	 * @return {Array} ridings sorted ascending by getStartTime()
	 */
	static #ridingsSortedByStartTime()
	{
		var sorted = ControlPanel.#ridings.slice()
		sorted.sort((a, b) => a.getStartTime() - b.getStartTime())
		return sorted
	}

	/**
	 * #drawReportingOrder renders every riding in the order its results actually get decided,
	 * with move-up/move-down controls that swap two ridings' start times (the set of time slots
	 * stays fixed; only which riding sits in which slot changes). This is what actually drives the
	 * Seat Projection chart, unlike the Running Order panel below it.
	 */
	static #drawReportingOrder()
	{
		var sorted = ControlPanel.#ridingsSortedByStartTime()

		var tmp = ""
		for(var i1 = 0; i1 < sorted.length; i1++)
		{
			var riding = sorted[i1]
			var selected = ControlPanel.#selectedRiding !== null && ControlPanel.#selectedRiding.getName() === riding.getName()

			tmp += '<div class="scheduleRow' + (selected ? " selected" : "") + '" data-index="' + i1 + '">'
				tmp += '<span class="scheduleTime">' + riding.getStartTime() + 's</span>'
				tmp += '<span class="scheduleRiding" data-riding="' + riding.getName() + '">' + riding.getName() + '</span>'
				tmp += '<input type="button" class="moveUp" value="&#9650;">'
				tmp += '<input type="button" class="moveDown" value="&#9660;">'
			tmp += '</div>'
		}

		ControlPanel.#reportingOrderList.html(tmp)

		ControlPanel.#reportingOrderList.find(".scheduleRiding").on("click", function()
		{
			ControlPanel.#selectRidingByName($(this).data("riding"))
		})

		ControlPanel.#reportingOrderList.find(".moveUp").on("click", function()
		{
			var index = parseInt($(this).closest(".scheduleRow").data("index"))
			ControlPanel.#swapStartTimes(sorted, index, index - 1)
		})

		ControlPanel.#reportingOrderList.find(".moveDown").on("click", function()
		{
			var index = parseInt($(this).closest(".scheduleRow").data("index"))
			ControlPanel.#swapStartTimes(sorted, index, index + 1)
		})
	}

	/**
	 * #swapStartTimes exchanges two ridings' start times - the same slot-swap pattern used by the
	 * Running Order's move buttons, applied here to when a riding's results are decided instead of
	 * to display scheduling. Each riding's own steps (and final result) are untouched; only the
	 * absolute time they play out at moves.
	 *
	 * @param {Array} sortedRidings the array #drawReportingOrder rendered from
	 * @param {integer} i1 index of the row being moved
	 * @param {integer} i2 index it's swapping with
	 */
	static #swapStartTimes(sortedRidings, i1, i2)
	{
		if(i2 < 0 || i2 >= sortedRidings.length)
		{
			return
		}

		var t1 = sortedRidings[i1].getStartTime()
		var t2 = sortedRidings[i2].getStartTime()
		sortedRidings[i1].setStartTime(t2)
		sortedRidings[i2].setStartTime(t1)

		ControlPanel.#afterReportingOrderChange()
	}

	/**
	 * #rerollReportingOrder shuffles which riding is assigned to which start-time slot - the set of
	 * slot times stays identical, only the riding-to-slot assignment is re-randomized.
	 */
	static #rerollReportingOrder()
	{
		var startTimes = []
		for(var i1 = 0; i1 < ControlPanel.#ridings.length; i1++)
		{
			startTimes.push(ControlPanel.#ridings[i1].getStartTime())
		}

		for(var i1 = startTimes.length - 1; i1 > 0; i1--)
		{
			var j = Math.floor(Math.random() * (i1 + 1))
			var tmp = startTimes[i1]
			startTimes[i1] = startTimes[j]
			startTimes[j] = tmp
		}

		for(var i1 = 0; i1 < ControlPanel.#ridings.length; i1++)
		{
			ControlPanel.#ridings[i1].setStartTime(startTimes[i1])
		}

		ControlPanel.#afterReportingOrderChange()
	}

	/**
	 * #afterReportingOrderChange refreshes everything downstream of riding start times: the display
	 * schedule needs rebuilding from scratch (RidingPools' active-window timing depends on start
	 * times), and the chart/stats need to reflect the new timing too.
	 */
	static #afterReportingOrderChange()
	{
		ControlPanel.#reroll()
		ControlPanel.#drawReportingOrder()
		ControlPanel.#drawStatsTable()
	}

	/**
	 * #drawChart plots each party's projected seat count over the length of the broadcast, with
	 * numeric axes (seats on Y, seconds on X) and a dashed "Ridings Reporting" reference line -
	 * since ridings start reporting at different times, seats can't (and shouldn't look like they)
	 * all become decided at once; the reference line makes that ramp-up explicit instead of just
	 * leaving the party lines looking like they mysteriously start low and climb.
	 */
	static #drawChart()
	{
		var ctx = ControlPanel.#chartCanvas.getContext("2d")
		var width = ControlPanel.#chartCanvas.width
		var height = ControlPanel.#chartCanvas.height

		ctx.clearRect(0, 0, width, height)

		var marginLeft = 45
		var marginRight = 10
		var marginTop = 10
		var marginBottom = 25
		var plotWidth = width - marginLeft - marginRight
		var plotHeight = height - marginTop - marginBottom

		var partyList = Object.values(ControlPanel.#parties)
		var endTime = ControlPanel.#schedule.endTime || 1
		var step = Math.max(1, Math.floor(endTime / plotWidth))
		var maxSeats = ControlPanel.#ridings.length || 1

		var series = {}
		for(var i1 = 0; i1 < partyList.length; i1++)
		{
			series[partyList[i1].getKey()] = []
		}
		var reportingSeries = []
		var pointCount = 0

		for(var time = 0; time <= endTime; time += step)
		{
			var seatCounts = SeatTally.compute(ControlPanel.#ridings, time)
			for(var i1 = 0; i1 < partyList.length; i1++)
			{
				var key = partyList[i1].getKey()
				series[key].push(seatCounts[key] || 0)
			}

			var reporting = 0
			for(var i1 = 0; i1 < ControlPanel.#ridings.length; i1++)
			{
				if(ControlPanel.#ridings[i1].getStartTime() <= time)
				{
					reporting++
				}
			}
			reportingSeries.push(reporting)
			pointCount++
		}

		var plotX = function(index)
		{
			return marginLeft + (index / (pointCount - 1 || 1)) * plotWidth
		}
		var plotY = function(value)
		{
			return marginTop + plotHeight - (value / maxSeats) * plotHeight
		}

		// Y-axis gridlines + seat count labels
		ctx.font = "11px sans-serif"
		var yTicks = 5
		for(var i1 = 0; i1 <= yTicks; i1++)
		{
			var seatValue = Math.round((maxSeats / yTicks) * i1)
			var y = plotY(seatValue)

			ctx.strokeStyle = "#eeeeee"
			ctx.lineWidth = 1
			ctx.beginPath()
			ctx.moveTo(marginLeft, y)
			ctx.lineTo(width - marginRight, y)
			ctx.stroke()

			ctx.fillStyle = "#888888"
			ctx.textAlign = "right"
			ctx.textBaseline = "middle"
			ctx.fillText(seatValue, marginLeft - 6, y)
		}

		// X-axis time labels (seconds)
		var xTicks = 5
		for(var i1 = 0; i1 <= xTicks; i1++)
		{
			var timeValue = Math.round((endTime / xTicks) * i1)
			var index = Math.round((pointCount - 1) * (i1 / xTicks))
			var x = plotX(index)

			ctx.fillStyle = "#888888"
			ctx.textAlign = "center"
			ctx.textBaseline = "top"
			ctx.fillText(timeValue + "s", x, height - marginBottom + 6)
		}

		// "Ridings Reporting" dashed reference line
		ctx.strokeStyle = "#aaaaaa"
		ctx.lineWidth = 1.5
		ctx.setLineDash([4, 4])
		ctx.beginPath()
		for(var i2 = 0; i2 < reportingSeries.length; i2++)
		{
			var x = plotX(i2)
			var y = plotY(reportingSeries[i2])

			if(i2 === 0)
			{
				ctx.moveTo(x, y)
			}
			else
			{
				ctx.lineTo(x, y)
			}
		}
		ctx.stroke()
		ctx.setLineDash([])

		// Party seat-count lines
		for(var i1 = 0; i1 < partyList.length; i1++)
		{
			var key = partyList[i1].getKey()
			var points = series[key]

			ctx.beginPath()
			ctx.strokeStyle = partyList[i1].getColour()
			ctx.lineWidth = 2

			for(var i2 = 0; i2 < points.length; i2++)
			{
				var x = plotX(i2)
				var y = plotY(points[i2])

				if(i2 === 0)
				{
					ctx.moveTo(x, y)
				}
				else
				{
					ctx.lineTo(x, y)
				}
			}

			ctx.stroke()
		}

		// Axis lines
		ctx.strokeStyle = "#999999"
		ctx.lineWidth = 1
		ctx.beginPath()
		ctx.moveTo(marginLeft, marginTop)
		ctx.lineTo(marginLeft, height - marginBottom)
		ctx.lineTo(width - marginRight, height - marginBottom)
		ctx.stroke()

		var legendHtml = '<span style="color:#aaaaaa; margin-right: 12px;">- - Ridings Reporting</span>'
		for(var i1 = 0; i1 < partyList.length; i1++)
		{
			legendHtml += '<span style="color:' + partyList[i1].getColour() + '; margin-right: 12px;">&#9632; ' + partyList[i1].getAbrv() + '</span>'
		}
		$("#chartLegend").html(legendHtml)
	}

	/**
	 * #drawStatsTable summarizes every riding (final margin, closest margin from a configurable
	 * step onward, and number of lead changes) into a sortable table, so the moderator can spot
	 * the most dramatic ridings at a glance. Clicking a row selects that riding in the step editor,
	 * same as clicking it in the running order.
	 */
	static #drawStatsTable()
	{
		var minStep = parseInt(ControlPanel.#statsMinStepInput.val())
		if(isNaN(minStep) || minStep < 0)
		{
			minStep = 0
		}

		var stats = RidingStats.computeAll(ControlPanel.#ridings, minStep)

		stats.sort((a, b) =>
		{
			var diff = a[ControlPanel.#statsSortField] - b[ControlPanel.#statsSortField]
			return ControlPanel.#statsSortAsc ? diff : -diff
		})

		var columns =
		[
			{key: "ridingName", label: "Riding", sortable: false},
			{key: "finalMargin", label: "Final Margin", sortable: true},
			{key: "closestMarginLate", label: "Closest Margin (late)", sortable: true},
			{key: "leadChanges", label: "Lead Changes", sortable: true},
		]

		var tmp = "<tr>"
		for(var i1 = 0; i1 < columns.length; i1++)
		{
			var arrow = ""
			if(columns[i1].sortable && ControlPanel.#statsSortField === columns[i1].key)
			{
				arrow = ControlPanel.#statsSortAsc ? " &#9650;" : " &#9660;"
			}
			tmp += '<th data-field="' + columns[i1].key + '" class="' + (columns[i1].sortable ? "sortable" : "") + '">' + columns[i1].label + arrow + '</th>'
		}
		tmp += "</tr>"

		for(var i1 = 0; i1 < stats.length; i1++)
		{
			var row = stats[i1]
			var selected = ControlPanel.#selectedRiding !== null && ControlPanel.#selectedRiding.getName() === row.ridingName

			tmp += '<tr class="statsRow' + (selected ? " selected" : "") + '" data-riding="' + row.ridingName + '">'
				tmp += '<td>' + row.ridingName + '</td>'
				tmp += '<td>' + row.finalMargin + '</td>'
				tmp += '<td>' + row.closestMarginLate + '</td>'
				tmp += '<td>' + row.leadChanges + '</td>'
			tmp += '</tr>'
		}

		ControlPanel.#statsTable.html(tmp)

		ControlPanel.#statsTable.find("th.sortable").on("click", function()
		{
			var field = $(this).data("field")
			if(ControlPanel.#statsSortField === field)
			{
				ControlPanel.#statsSortAsc = !ControlPanel.#statsSortAsc
			}
			else
			{
				ControlPanel.#statsSortField = field
				ControlPanel.#statsSortAsc = true
			}
			ControlPanel.#drawStatsTable()
		})

		ControlPanel.#statsTable.find(".statsRow").on("click", function()
		{
			ControlPanel.#selectRidingByName($(this).data("riding"))
		})
	}

	/**
	 * #drawList renders one running-order list (primary or secondary) with move-up/move-down
	 * controls that let the moderator swap which riding fills which time slot - the slot times
	 * themselves stay fixed (they're governed by real pool-availability timing), only the riding
	 * name assigned to each slot moves. Clicking a riding's name selects it in the step editor.
	 *
	 * @param {jQuery} container
	 * @param {Array} entries {time, ridingName}
	 */
	static #drawList(container, entries)
	{
		var tmp = ""
		for(var i1 = 0; i1 < entries.length; i1++)
		{
			var selected = ControlPanel.#selectedRiding !== null && ControlPanel.#selectedRiding.getName() === entries[i1].ridingName

			tmp += '<div class="scheduleRow' + (selected ? " selected" : "") + '" data-index="' + i1 + '">'
				tmp += '<span class="scheduleTime">' + entries[i1].time + 's</span>'
				tmp += '<span class="scheduleRiding" data-riding="' + entries[i1].ridingName + '">' + entries[i1].ridingName + '</span>'
				tmp += '<input type="button" class="moveUp" value="&#9650;">'
				tmp += '<input type="button" class="moveDown" value="&#9660;">'
			tmp += '</div>'
		}

		container.html(tmp)

		container.find(".scheduleRiding").on("click", function()
		{
			ControlPanel.#selectRidingByName($(this).data("riding"))
		})

		container.find(".moveUp").on("click", function()
		{
			var index = parseInt($(this).closest(".scheduleRow").data("index"))
			ControlPanel.#swap(entries, index, index - 1)
			ControlPanel.#drawList(container, entries)
		})

		container.find(".moveDown").on("click", function()
		{
			var index = parseInt($(this).closest(".scheduleRow").data("index"))
			ControlPanel.#swap(entries, index, index + 1)
			ControlPanel.#drawList(container, entries)
		})
	}

	/**
	 * #swap exchanges which riding fills two adjacent time slots.
	 *
	 * @param {Array} entries schedule.primary or schedule.secondary
	 * @param {integer} i1 index of the row being moved
	 * @param {integer} i2 index it's swapping with
	 */
	static #swap(entries, i1, i2)
	{
		if(i2 < 0 || i2 >= entries.length)
		{
			return
		}

		var tmp = entries[i1].ridingName
		entries[i1].ridingName = entries[i2].ridingName
		entries[i2].ridingName = tmp
	}

	/**
	 * #confirm locks in the (possibly edited) schedule and hands off to the moderator's onConfirm
	 * callback (SetUp.js's countdown/go-live step).
	 */
	static #confirm()
	{
		ControlPanel.#area.css("display", "none")
		ControlPanel.#onConfirm(ControlPanel.#schedule)
	}

	/**
	 * #compileVideo triggers VideoCompiler against the schedule as currently edited, without
	 * requiring the moderator to go live first.
	 */
	static #compileVideo()
	{
		VideoCompiler.compile(ControlPanel.#parties, ControlPanel.#ridings, ControlPanel.#schedule, $("#videoCompileStatus"))
	}

	/**
	 * #drawJumpList renders a small clickable chip per riding, as a fallback way to select a riding
	 * that isn't (yet) showing in either running-order list.
	 */
	static #drawJumpList()
	{
		var tmp = ""
		for(var i1 = 0; i1 < ControlPanel.#ridings.length; i1++)
		{
			var name = ControlPanel.#ridings[i1].getName()
			var selected = ControlPanel.#selectedRiding !== null && ControlPanel.#selectedRiding.getName() === name
			tmp += '<span class="ridingChip' + (selected ? " selected" : "") + '" data-riding="' + name + '">' + name + '</span>'
		}
		ControlPanel.#jumpList.html(tmp)

		ControlPanel.#jumpList.find(".ridingChip").on("click", function()
		{
			ControlPanel.#selectRidingByName($(this).data("riding"))
		})
	}

	/**
	 * #selectRidingByName looks up a riding by name and selects it - the common entry point used
	 * by clicks in the running order, the stats table, and the riding chip list.
	 *
	 * @param {string} name
	 */
	static #selectRidingByName(name)
	{
		for(var i1 = 0; i1 < ControlPanel.#ridings.length; i1++)
		{
			if(ControlPanel.#ridings[i1].getName() === name)
			{
				ControlPanel.#selectRiding(ControlPanel.#ridings[i1])
				return
			}
		}
	}

	/**
	 * #selectRiding makes `riding` the one shown in the step editor, and refreshes every view that
	 * highlights the current selection (running order, stats table, riding chips).
	 *
	 * @param {Riding} riding
	 */
	static #selectRiding(riding)
	{
		ControlPanel.#selectedRiding = riding
		ControlPanel.#ridingLabel.text(riding.getName())

		ControlPanel.#drawJumpList()
		ControlPanel.#drawReportingOrder()
		ControlPanel.#drawList(ControlPanel.#primaryList, ControlPanel.#schedule.primary)
		ControlPanel.#drawList(ControlPanel.#secondaryList, ControlPanel.#schedule.secondary)
		ControlPanel.#drawStepEditor()
		ControlPanel.#drawStatsTable()
	}

	/**
	 * #candidatesOf returns the selected riding's candidates in a stable order (sorted by their
	 * vote count at the riding's own start time, i.e. step 0) so the table doesn't reshuffle rows
	 * every redraw.
	 *
	 * @return {Array} candidates of ControlPanel.#selectedRiding
	 */
	static #candidatesOf()
	{
		return ControlPanel.#selectedRiding.getCandidateVote(ControlPanel.#selectedRiding.getStartTime())
	}

	/**
	 * #drawStepEditor renders the selected riding's candidates x steps table, with one editable
	 * number input per step so the moderator can hand-edit any individual value.
	 */
	static #drawStepEditor()
	{
		ControlPanel.#drawStepChart()

		if(ControlPanel.#selectedRiding === null)
		{
			ControlPanel.#stepEditorTable.html("")
			return
		}

		var candidates = ControlPanel.#candidatesOf()

		var maxSteps = 0
		for(var i1 = 0; i1 < candidates.length; i1++)
		{
			maxSteps = Math.max(maxSteps, candidates[i1].getVoteCount().length)
		}

		// The last step is the declared final result - it can't be rerolled or hand-edited, since
		// nothing about "how we got there" is allowed to change what the result actually was.
		var lastEditableStep = maxSteps - 2

		ControlPanel.#stepEditorFrom.attr("max", Math.max(1, lastEditableStep + 1))
		ControlPanel.#stepEditorTo.attr("max", Math.max(1, lastEditableStep + 1))
		if(!ControlPanel.#stepEditorTo.val() || parseInt(ControlPanel.#stepEditorTo.val()) > lastEditableStep + 1)
		{
			ControlPanel.#stepEditorTo.val(Math.max(1, lastEditableStep + 1))
		}

		var tmp = "<tr><th>Candidate</th>"
		for(var s = 0; s < maxSteps; s++)
		{
			tmp += "<th>Step " + (s + 1) + (s === maxSteps - 1 ? " &#128274;" : "") + "</th>"
		}
		tmp += "</tr>"

		for(var i1 = 0; i1 < candidates.length; i1++)
		{
			var candidate = candidates[i1]
			var party = ControlPanel.#parties[candidate.getParty()]
			var partyName = party ? party.getAbrv() : candidate.getParty()

			tmp += '<tr><td>' + partyName + ' ' + candidate.getName() + '</td>'

			var steps = candidate.getVoteCount()
			for(var s = 0; s < maxSteps; s++)
			{
				if(s < steps.length)
				{
					var isFinalStep = s === steps.length - 1
					tmp += '<td><input type="number" min="0" class="stepInput' + (isFinalStep ? " stepLocked" : "") + '" data-candidate="' + i1 + '" data-step="' + s + '" value="' + steps[s] + '"' + (isFinalStep ? ' disabled title="The final step is the declared result and can\'t be changed."' : '') + '></td>'
				}
				else
				{
					tmp += '<td>-</td>'
				}
			}
			tmp += '</tr>'
		}

		ControlPanel.#stepEditorTable.html(tmp)

		ControlPanel.#stepEditorTable.find(".stepInput").on("change", function()
		{
			var candidateIndex = parseInt($(this).data("candidate"))
			var stepIndex = parseInt($(this).data("step"))
			var value = parseInt($(this).val()) || 0
			candidates[candidateIndex].setVoteCountAt(stepIndex, value)
			ControlPanel.#drawStepChart()
			ControlPanel.#drawChart()
			ControlPanel.#drawStatsTable()
		})
	}

	/**
	 * #drawStepChart plots the selected riding's own candidates x steps as a small line chart (vote
	 * count per step, one line per candidate), with numeric axes - a visual complement to the raw
	 * numbers in the table below, so you can actually see the shape of a single riding's race while
	 * editing or rerolling it, rather than just the aggregated national Seat Projection above.
	 */
	static #drawStepChart()
	{
		var ctx = ControlPanel.#stepChartCanvas.getContext("2d")
		var width = ControlPanel.#stepChartCanvas.width
		var height = ControlPanel.#stepChartCanvas.height

		ctx.clearRect(0, 0, width, height)

		if(ControlPanel.#selectedRiding === null)
		{
			$("#stepChartLegend").html("")
			return
		}

		var candidates = ControlPanel.#candidatesOf()

		var maxSteps = 0
		var maxVotes = 1
		for(var i1 = 0; i1 < candidates.length; i1++)
		{
			var steps = candidates[i1].getVoteCount()
			maxSteps = Math.max(maxSteps, steps.length)
			for(var s = 0; s < steps.length; s++)
			{
				maxVotes = Math.max(maxVotes, steps[s])
			}
		}

		var marginLeft = 55
		var marginRight = 10
		var marginTop = 10
		var marginBottom = 22
		var plotWidth = width - marginLeft - marginRight
		var plotHeight = height - marginTop - marginBottom

		var plotX = function(index)
		{
			return marginLeft + (index / (maxSteps - 1 || 1)) * plotWidth
		}
		var plotY = function(value)
		{
			return marginTop + plotHeight - (value / maxVotes) * plotHeight
		}

		ctx.font = "11px sans-serif"

		// Y-axis gridlines + vote count labels
		var yTicks = 4
		for(var i1 = 0; i1 <= yTicks; i1++)
		{
			var voteValue = Math.round((maxVotes / yTicks) * i1)
			var y = plotY(voteValue)

			ctx.strokeStyle = "#eeeeee"
			ctx.lineWidth = 1
			ctx.beginPath()
			ctx.moveTo(marginLeft, y)
			ctx.lineTo(width - marginRight, y)
			ctx.stroke()

			ctx.fillStyle = "#888888"
			ctx.textAlign = "right"
			ctx.textBaseline = "middle"
			ctx.fillText(voteValue, marginLeft - 6, y)
		}

		// X-axis step labels
		for(var s = 0; s < maxSteps; s++)
		{
			var x = plotX(s)

			ctx.fillStyle = "#888888"
			ctx.textAlign = "center"
			ctx.textBaseline = "top"
			ctx.fillText(s + 1, x, height - marginBottom + 6)
		}

		// One line per candidate
		var legendHtml = ""
		for(var i1 = 0; i1 < candidates.length; i1++)
		{
			var candidate = candidates[i1]
			var party = ControlPanel.#parties[candidate.getParty()]
			var colour = party ? party.getColour() : "#333333"
			var abrv = party ? party.getAbrv() : candidate.getParty()
			var steps = candidate.getVoteCount()

			ctx.beginPath()
			ctx.strokeStyle = colour
			ctx.lineWidth = 2

			for(var s = 0; s < steps.length; s++)
			{
				var x = plotX(s)
				var y = plotY(steps[s])

				if(s === 0)
				{
					ctx.moveTo(x, y)
				}
				else
				{
					ctx.lineTo(x, y)
				}
			}
			ctx.stroke()

			legendHtml += '<span style="color:' + colour + '; margin-right: 12px;">&#9632; ' + abrv + ' ' + candidate.getName() + '</span>'
		}
		$("#stepChartLegend").html(legendHtml)

		// Axis lines
		ctx.strokeStyle = "#999999"
		ctx.lineWidth = 1
		ctx.beginPath()
		ctx.moveTo(marginLeft, marginTop)
		ctx.lineTo(marginLeft, height - marginBottom)
		ctx.lineTo(width - marginRight, height - marginBottom)
		ctx.stroke()
	}

	/**
	 * #rerollSelectedRange rerolls whichever step range is currently entered in the "from"/"to"
	 * inputs (1-based in the UI, converted to 0-based indices here).
	 */
	static #rerollSelectedRange()
	{
		var fromIndex = parseInt(ControlPanel.#stepEditorFrom.val()) - 1
		var toIndex = parseInt(ControlPanel.#stepEditorTo.val()) - 1
		ControlPanel.#rerollSteps(fromIndex, toIndex)
	}

	/**
	 * #rerollAllSteps rerolls every rerollable step of the selected riding - a shorthand for
	 * selecting the full range (excluding the final, locked step - see #rerollSteps).
	 */
	static #rerollAllSteps()
	{
		if(ControlPanel.#selectedRiding === null)
		{
			return
		}

		ControlPanel.#rerollSteps(0, Number.MAX_SAFE_INTEGER)
	}

	/**
	 * #rerollAllRidings rerolls every rerollable step (final result still excluded) for every
	 * riding at once - the same operation #rerollAllSteps applies to just the selected riding, run
	 * across the entire election.
	 */
	static #rerollAllRidings()
	{
		for(var i1 = 0; i1 < ControlPanel.#ridings.length; i1++)
		{
			ControlPanel.#rerollRidingFullRange(ControlPanel.#ridings[i1])
		}

		ControlPanel.#drawStepEditor()
		ControlPanel.#drawChart()
		ControlPanel.#drawStatsTable()
	}

	/**
	 * #rerollRidingFullRange rerolls every candidate's rerollable steps (all but the locked final
	 * step) for a single riding - shared by #rerollAllSteps (selected riding only) and
	 * #rerollAllRidings (every riding).
	 *
	 * @param {Riding} riding
	 */
	static #rerollRidingFullRange(riding)
	{
		var candidates = riding.getCandidateVote(riding.getStartTime())
		for(var i1 = 0; i1 < candidates.length; i1++)
		{
			var lastEditableIndex = candidates[i1].getVoteCount().length - 2
			if(lastEditableIndex >= 0)
			{
				ControlPanel.#rerollCandidateSteps(candidates[i1], 0, lastEditableIndex)
			}
		}
	}

	/**
	 * #rerollSteps regenerates every candidate's cumulative vote counts across [fromIndex,
	 * toIndex] in the selected riding, then refreshes the table, chart, and stats.
	 *
	 * The final step is always excluded, however large `toIndex` is - it's the declared result of
	 * the riding, and rerolling/hand-editing is only meant to change the drama of how the count
	 * gets there, never the result itself.
	 *
	 * @param {integer} fromIndex 0-based first step to reroll (inclusive)
	 * @param {integer} toIndex 0-based last step to reroll (inclusive) - clamped below the final step
	 */
	static #rerollSteps(fromIndex, toIndex)
	{
		if(ControlPanel.#selectedRiding === null)
		{
			return
		}

		if(isNaN(fromIndex) || isNaN(toIndex) || fromIndex < 0 || toIndex < fromIndex)
		{
			return
		}

		var candidates = ControlPanel.#candidatesOf()

		for(var i1 = 0; i1 < candidates.length; i1++)
		{
			var candidate = candidates[i1]
			var lastEditableIndex = candidate.getVoteCount().length - 2
			var clampedTo = Math.min(toIndex, lastEditableIndex)

			if(clampedTo >= fromIndex)
			{
				ControlPanel.#rerollCandidateSteps(candidate, fromIndex, clampedTo)
			}
		}

		ControlPanel.#drawStepEditor()
		ControlPanel.#drawChart()
		ControlPanel.#drawStatsTable()
	}

	/**
	 * #rerollCandidateSteps regenerates one candidate's cumulative vote counts across [fromIndex,
	 * toIndex] with a random monotonically-increasing walk. If a fixed value exists right after the
	 * rerolled range, the walk is aimed to land on it (so the progression still reconnects smoothly
	 * with whatever wasn't rerolled); otherwise it just keeps growing by a random amount each step.
	 *
	 * @param {Candidate} candidate
	 * @param {integer} fromIndex 0-based first step to reroll (inclusive)
	 * @param {integer} toIndex 0-based last step to reroll (inclusive)
	 */
	static #rerollCandidateSteps(candidate, fromIndex, toIndex)
	{
		var steps = candidate.getVoteCount()
		var lastIndex = steps.length - 1

		var clampedTo = Math.min(toIndex, lastIndex)
		var count = clampedTo - fromIndex + 1
		if(count <= 0)
		{
			return
		}

		var previous = fromIndex > 0 ? steps[fromIndex - 1] : 0
		var anchor = clampedTo < lastIndex ? steps[clampedTo + 1] : null

		for(var i1 = 0; i1 < count; i1++)
		{
			var index = fromIndex + i1
			var remaining = count - i1
			var target

			if(anchor !== null)
			{
				var averageStep = Math.max(1, (anchor - previous) / remaining)
				target = Math.round(previous + averageStep * (0.5 + Math.random()))
				target = Math.min(target, anchor)
			}
			else
			{
				var growth = Math.round(previous * (0.05 + Math.random() * 0.35)) + Math.round(Math.random() * 500)
				target = previous + Math.max(1, growth)
			}

			candidate.setVoteCountAt(index, target)
			previous = target
		}
	}
}
