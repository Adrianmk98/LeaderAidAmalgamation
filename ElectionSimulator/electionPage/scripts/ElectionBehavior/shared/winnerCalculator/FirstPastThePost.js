/**
 * FirstPastThePost finds the winner of a riding using first past the post
 */
class FirstPastThePost extends WinnerCalculator
{

	/**
	 * calculate returns the winner of a riding
	 *
	 * @return {array} array of party id strings of winning party
	 */
	calculate(candidates)
	{
		var largest = candidates[0];

		for(var i1 = 1; i1 < candidates.length; i1++)
		{
			if(candidates[i1].votes > largest.votes)
			{
				largest = candidates[i1]
			}
		}

		if(largest.votes === 0)
		{
			return []
		}
		return [largest.getParty()];
	}
}