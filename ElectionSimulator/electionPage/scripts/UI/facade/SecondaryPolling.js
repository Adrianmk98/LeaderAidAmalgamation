class SecondaryPolling extends Facade
{
	static area = $("#secondaryPoll").children().last();
	static ridingName = $("#ridingName")

	static #candidates;

	static #tmp = false;

	constructor()
	{
		super()
	}


	/**
	 * generates secondary polling area html
	 *
	 * @param {Riding} riding that will displayed in the primary polling area
	 * @param {parties} parties used to update colours of html elements
	 * @param {time} time is the current time value
	 */
	draw(riding, parties, time)
	{
		SecondaryPolling.#candidates = riding.getCandidateVote(time)
		var tmp = ""
		var candidate;
		for(var i1 = 0; i1 < SecondaryPolling.#candidates.length; i1++)
		{
			candidate = SecondaryPolling.#candidates[i1]
			tmp += this.#draw(candidate, parties[candidate.getParty()].getAbrv(), riding.votes, i1 == 0)
		}
		SecondaryPolling.area.html(tmp)
		SecondaryPolling.ridingName.text(riding.getName())
	}

	/**
	 * #draw method returns string of candidate box for HTML
	 *
	 * @param {Candidate} candidate is a candidate object that stores key candidate information
	 * @param {partyName} partyName is the name of the party
	 *
	 * @return {String} string format of html of a candidate box
	 */
	#draw(candidate, partyName, totalVoteCount, winner)
	{
		var votePercent;
		if(totalVoteCount === 0)
		{
			votePercent = 0
		}
		else
		{
			votePercent = Math.round(candidate.votes / totalVoteCount * 100)
		}

		var tmp = ""

		tmp += '<div class="candidate" id="'+candidate.getParty()+'">'
			tmp += '<img src="facesteals/'+candidate.getFaceSteal()+'">'
			tmp += '<div id="party" class="partyColour">'
				tmp += '<div>'+partyName+'</div>'
			tmp += '</div>'
			tmp += '<div id="name">'
				tmp += '<div>U/'+candidate.getName()+'</div>'
			tmp += '</div>'
			tmp += '<div id="vote">'
				tmp += '<div>'+(votePercent)+'%</div>'
				tmp += '<div>'+candidate.votes+'</div>'
			tmp += '</div>'
		tmp += '</div>'

		return tmp
	}

	/**
	 * update the Secondary polling area
	 *
	 * @param {Riding} riding that will displayed in the primary polling area
	 * @param {parties} parties used to update colours of html elements
	 * @param {time} time is the current time value
	 */
	update(riding, parties, time)
	{
		SecondaryPolling.#candidates = riding.getCandidateVote(time)
		var tmp = ""
		var candidate;
		for(var i1 = 0; i1 < SecondaryPolling.#candidates.length; i1++)
		{
			candidate = SecondaryPolling.#candidates[i1]
			tmp += this.#draw(candidate, parties[candidate.getParty()].getAbrv(), riding.votes, i1 == 0)
		}
		SecondaryPolling.area.html(tmp)
		SecondaryPolling.ridingName.children().first().text(riding.getName())
	}
}