/**
 * MajorityMeter Facade updates majority meter
 */
class MajorityMeter extends Facade
{
	static area = $("#majorityMeter #polling");

	static #quorum;
	static #allParties = []; // Store all parties for reference

	/**
	 * Draw method sets up party bars
	 *
	 * @param {array} parties is an array of party ids
	 * @param {integer} totalSeatCount is number of seats that could be won
	 */
	draw(parties, totalSeatCount)
	{
		// Store all parties for later reference
		MajorityMeter.#allParties = [...parties];
		
		// Initially create bars in the provided order
		var tmp = ""
		for(var i1 = 0; i1 < parties.length; i1++)
		{
			tmp += '<div id="'+parties[i1]+'" class="partyColour progress"></div>'
		}

		MajorityMeter.area.html(tmp)

		MajorityMeter.#quorum = Math.ceil(totalSeatCount/2) + 1

		$("#majorityMeter").find("#overlay").find("div:nth-child(2)").text(MajorityMeter.#quorum + " seats")
	}

	/**
	 * update all party bars
	 *
	 * @param {array} ridings is an array of Riding that will be used to calculate winner for each riding
	 * @param {integer} time is used to update each ridings seat count
	 */
	update(ridings, time)
	{
		var seatCounts = SeatTally.compute(ridings, time)

		// Initialize seat counts for all parties not currently holding a seat
		for(var i1 = 0; i1 < MajorityMeter.#allParties.length; i1++)
		{
			if(seatCounts[MajorityMeter.#allParties[i1]] === undefined)
			{
				seatCounts[MajorityMeter.#allParties[i1]] = 0;
			}
		}

		// Sort parties by seat count (highest first)
		var sortedParties = Object.keys(seatCounts).sort((a, b) => {
			return seatCounts[b] - seatCounts[a];
		});

		// Clear current width styles
		$("#majorityMeter").find("#polling").children().css("width", "0%");

		// Reorder DOM elements based on sorted results
		var container = $("#majorityMeter").find("#polling");
		var elements = [];
		
		// Collect all party elements
		for(var i1 = 0; i1 < sortedParties.length; i1++)
		{
			var element = container.find("#" + sortedParties[i1]);
			if(element.length > 0) {
				elements.push(element.detach());
			}
		}
		
		// Re-append in sorted order
		for(var i1 = 0; i1 < elements.length; i1++)
		{
			container.append(elements[i1]);
		}

		// Update widths for sorted parties
		var percent;
		for(var i1 = 0; i1 < sortedParties.length; i1++)
		{
			if(seatCounts[sortedParties[i1]] > 0) {
				percent = seatCounts[sortedParties[i1]] / MajorityMeter.#quorum * 100 * 0.68;
				$("#majorityMeter").find("#polling").find("#"+sortedParties[i1]).css("width", Math.min(percent, 95)+"%");
			}
		}
	}
}