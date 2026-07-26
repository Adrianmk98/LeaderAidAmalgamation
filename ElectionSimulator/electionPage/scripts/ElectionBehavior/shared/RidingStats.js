/**
 * RidingStats summarizes each riding's step-by-step results into moderator-friendly stats - how
 * close the race gets late in the count, and how many times the lead changes hands - so it's easy
 * to spot which ridings are worth featuring for drama in the Control Panel.
 */
class RidingStats
{
	/**
	 * compute summarizes one riding across every one of its polling steps.
	 *
	 * @param {Riding} riding
	 * @param {integer} minStep 0-based step index from which the "late margin" is tracked
	 *
	 * @return {Object} {ridingName, steps, finalMargin, closestMarginLate, leadChanges}
	 */
	static compute(riding, minStep)
	{
		var maxSteps = 0
		var firstStepCandidates = riding.getCandidateVote(riding.getStartTime())
		for(var i1 = 0; i1 < firstStepCandidates.length; i1++)
		{
			maxSteps = Math.max(maxSteps, firstStepCandidates[i1].getVoteCount().length)
		}

		var previousLeader = null
		var leadChanges = 0
		var closestMarginLate = null
		var finalMargin = 0

		for(var s = 0; s < maxSteps; s++)
		{
			var time = riding.getStartTime() + s * riding.getDeltaTime()
			var candidates = riding.getCandidateVote(time)

			var leader = candidates[0]
			var runnerUp = candidates.length > 1 ? candidates[1] : null
			var margin = runnerUp !== null ? leader.votes - runnerUp.votes : leader.votes

			if(previousLeader !== null && leader.getParty() !== previousLeader)
			{
				leadChanges++
			}
			previousLeader = leader.getParty()

			if(s >= minStep)
			{
				if(closestMarginLate === null || margin < closestMarginLate)
				{
					closestMarginLate = margin
				}
			}

			finalMargin = margin
		}

		return {
			ridingName: riding.getName(),
			steps: maxSteps,
			finalMargin: finalMargin,
			closestMarginLate: closestMarginLate === null ? finalMargin : closestMarginLate,
			leadChanges: leadChanges,
		}
	}

	/**
	 * computeAll summarizes every riding.
	 *
	 * @param {Array} ridings array of Riding
	 * @param {integer} minStep 0-based step index from which the "late margin" is tracked
	 *
	 * @return {Array} one stats object per riding, in the same order as `ridings`
	 */
	static computeAll(ridings, minStep)
	{
		var results = []
		for(var i1 = 0; i1 < ridings.length; i1++)
		{
			results.push(RidingStats.compute(ridings[i1], minStep))
		}
		return results
	}
}
