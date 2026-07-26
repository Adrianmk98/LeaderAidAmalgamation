/**
 * SeatTally computes each party's seat count at a given simulation time - the tally logic shared by
 * SeatCount, MajorityMeter, and the Control Panel's seat-projection chart.
 */
class SeatTally
{
	/**
	 * compute tallies the winning party of every riding at a given time.
	 *
	 * @param {Array} ridings array of Riding
	 * @param {float} time current simulation time
	 *
	 * @return {Object} partyKey -> seat count
	 */
	static compute(ridings, time)
	{
		var seatCounts = {}

		for(var i1 = 0; i1 < ridings.length; i1++)
		{
			ridings[i1].getCandidateVote(time)
			var winner = ridings[i1].getWinner()

			for(var i2 = 0; i2 < winner.length; i2++)
			{
				if(seatCounts[winner[i2]] === undefined)
				{
					seatCounts[winner[i2]] = 1
				}
				else
				{
					seatCounts[winner[i2]] += 1
				}
			}
		}

		return seatCounts
	}
}
