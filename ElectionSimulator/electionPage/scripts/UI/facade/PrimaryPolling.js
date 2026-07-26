class PrimaryPolling extends Facade
{
	static area = $("#main");
	static ridingName = $("#header")

	static #candidates;

	constructor()
	{
		super()
	}

	/**
	 * generates primary polling area html
	 *
	 * @param {Riding} riding that will displayed in the primary polling area
	 * @param {parties} parties used to update colours of html elements
	 * @param {time} time is the current time value
	 */
	draw(riding, parties, time)
	{
		PrimaryPolling.#candidates = riding.getCandidateVote(time)
		var tmp = ""
		var candidate;
		for(var i1 = 0; i1 < PrimaryPolling.#candidates.length; i1++)
		{
			candidate = PrimaryPolling.#candidates[i1]
			tmp += this.#draw(candidate, parties[candidate.getParty()].getAbrv(), riding.votes, i1 == 0)
		}
		PrimaryPolling.area.html(tmp)
		PrimaryPolling.ridingName.children().first().text(riding.getName())
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
		var tmp = ""

		tmp += '<div id="'+ candidate.getParty() +'" class="candidate partyColourBorder">'
			tmp += '<img src="facesteals/'+ candidate.getFaceSteal() +'">'
			tmp += '<div class="party partyColour">'+ partyName +'</div>'
			tmp += '<div class="name">U/'+ candidate.getName() +'</div>'
			tmp += '<div class="cover"></div>'
			tmp += '<div class="vote">'
				tmp += '<div class="percent">'

					var votePercent;
					if(totalVoteCount === 0)
					{
						votePercent = 0
					}
					else
					{
						votePercent = Math.round(candidate.votes / totalVoteCount * 100)
					}
					tmp += '<h1>'+ votePercent +'%</h1>'
					tmp += '<div id="progressBar">'
						tmp += '<div style="width: '+ votePercent +'%;" class="progress partyColour"></div>'
					tmp += '</div>'
				tmp += '</div>'
				tmp += '<div class="voteCount '
				if(winner)
				{
					tmp += 'winner'
				}
					tmp+='">'

					tmp += '<h3>' + candidate.votes + '</h3>'
				if(winner)
				{
					if(PrimaryPolling.#candidates.length >= 2)
					{
						if(PrimaryPolling.#candidates[0].votes - PrimaryPolling.#candidates[1].votes === 0)
						{
							tmp += '<h4>'+ 'Tie' + '</h4>'
						}
						else
						{
							tmp += '<h4>'+ (PrimaryPolling.#candidates[0].votes - PrimaryPolling.#candidates[1].votes) +' lead'+'</h4>'
						}
					}
					else
					{
						//tmp += '<h4>'+ totalVoteCount +' lead'+'</h4>'
					}
				}
				tmp += '</div>'
			tmp += '</div>'
			tmp += '<div class="bottom"></div>'
		tmp += '</div>'

		return tmp
	}

	/**
	 * update the primary polling area
	 *
	 * @param {Riding} riding that will displayed in the primary polling area
	 * @param {parties} parties used to update colours of html elements
	 * @param {time} time is the current time value
	 */
	update(riding, parties, time)
	{
		PrimaryPolling.#candidates = riding.getCandidateVote(time)
		var tmp = ""
		var candidate;
		for(var i1 = 0; i1 < PrimaryPolling.#candidates.length; i1++)
		{
			candidate = PrimaryPolling.#candidates[i1]
			tmp += this.#draw(candidate, parties[candidate.getParty()].getAbrv(), riding.votes, i1 == 0)
		}
		PrimaryPolling.area.html(tmp)
		PrimaryPolling.ridingName.children().first().text(riding.getName())
	}
}
