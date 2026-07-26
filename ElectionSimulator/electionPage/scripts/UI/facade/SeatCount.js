/**
 * SeatCount class updates the seat count footer
 */
class SeatCount extends Facade
{
	static area = $("#footer");
	static #allParties = []; // Store all parties for reference

	/**
	 * draws a party seat count boxes
	 *
	 * @param {array} parties is an array of Party that will be visible
	 */
	draw(parties)
	{
		// Store all parties for later reference
		SeatCount.#allParties = [...parties];

		var tmp = ""
		for(var i1 = 0; i1 < parties.length; i1++)
		{
			tmp += this.#draw(parties[i1])
			if(i1 != parties.length - 1)
			{
				tmp += this.#separator()
			}
		}

		SeatCount.area.html(tmp)
	}

	/**
	 * #draw returns a string of the HTML of a party
	 *
	 * @param {Party} party is a Party object used to create a seat count box
	 *
	 * @return {String} HTML of a party
	 */
	#draw(party)
	{
		var tmp = ""

		tmp += '<div id="'+party.getKey()+'" class="party partyColour">'
			tmp += '<div class="name">'+party.getAbrv()+'</div>'
			tmp += '<div class="seat">0</div>'
		tmp += '</div>'

		return tmp;
	}

	/**
	 * #separator returns html string 
	 */
	#separator()
	{
		return '<div class="separator"></div>'
	}

	/**
	 * update the already drawn party seat count boxes
	 *
	 * @param {array} ridings is an array of Riding that will be used to calculate winner for each riding
	 * @param {integer} time is used to update each ridings seat count
	 */
	update(ridings, time)
	{
		var seatCounts = SeatTally.compute(ridings, time)

		// Initialize seat counts for all parties not currently holding a seat
		for(var i1 = 0; i1 < SeatCount.#allParties.length; i1++)
		{
			if(seatCounts[SeatCount.#allParties[i1].getKey()] === undefined)
			{
				seatCounts[SeatCount.#allParties[i1].getKey()] = 0;
			}
		}

		// Sort parties by seat count (highest first)
		var sortedParties = SeatCount.#allParties.sort((a, b) => {
			var aSeats = seatCounts[a.getKey()] || 0;
			var bSeats = seatCounts[b.getKey()] || 0;
			return bSeats - aSeats;
		});

		// Rebuild the HTML in sorted order
		var tmp = ""
		for(var i1 = 0; i1 < sortedParties.length; i1++)
		{
			tmp += this.#draw(sortedParties[i1])
			if(i1 != sortedParties.length - 1)
			{
				tmp += this.#separator()
			}
		}

		// Replace the HTML content
		SeatCount.area.html(tmp)

		// Update seat counts for all parties
		for(var i1 = 0; i1 < sortedParties.length; i1++)
		{
			var partyKey = sortedParties[i1].getKey();
			var seats = seatCounts[partyKey] || 0;
			$("#"+partyKey+".party").children().last().text(seats);
		}
	}
}