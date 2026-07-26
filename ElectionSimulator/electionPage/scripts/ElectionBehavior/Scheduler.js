/**
 * Scheduler pre-computes, once, which riding is featured on the primary/secondary panel at every
 * tick of the broadcast. RidingPools.selectActive() is the only source of randomness anywhere in
 * the simulator (every vote total is fixed by the riding CSV, interpolated deterministically) - by
 * rolling that choice for the whole run up front we get a fully deterministic schedule that can be
 * previewed, reordered by a moderator on the Control Panel, and then replayed identically whether
 * live or compiled straight to video.
 */
class Scheduler
{
	static PRIMARY_POOL_MAX = 5
	static SECONDARY_POOL_MAX = NaN

	/**
	 * build simulates pool membership/selection for the whole broadcast ahead of time.
	 *
	 * @param {Array} ridings array of Riding
	 * @param {integer} primaryMax max concurrently-active ridings in the primary pool
	 * @param {integer} secondaryMax max concurrently-active ridings in the secondary pool
	 * @param {float} primaryDuration seconds between primary panel switches
	 * @param {float} secondaryDuration seconds between secondary panel switches
	 *
	 * @return {Object} {primary: [{time, ridingName}], secondary: [{time, ridingName}], endTime}
	 */
	static build(ridings, primaryMax, secondaryMax, primaryDuration, secondaryDuration)
	{
		var primaryPool = new RidingPools(primaryMax, ridings)
		var secondaryPool = new RidingPools(secondaryMax, ridings)

		var primary = []
		var secondary = []

		var endTime = Scheduler.#endTime(ridings)

		for(var time = 0; time <= endTime; time++)
		{
			primaryPool.updatePool(time)
			secondaryPool.updatePool(time)

			if(primaryPool.active.length > 0 && time % primaryDuration === 0)
			{
				primary.push({time: time, ridingName: primaryPool.selectActive().getName()})
			}

			if(secondaryPool.active.length > 0 && time % secondaryDuration === 0)
			{
				secondary.push({time: time, ridingName: secondaryPool.selectActive().getName()})
			}
		}

		return {primary: primary, secondary: secondary, endTime: endTime}
	}

	/**
	 * ridingsByName builds a name -> Riding lookup map, used to resolve schedule entries back into
	 * Riding objects.
	 *
	 * @param {Array} ridings array of Riding
	 *
	 * @return {Map}
	 */
	static ridingsByName(ridings)
	{
		var map = new Map()
		for(var i1 = 0; i1 < ridings.length; i1++)
		{
			map.set(ridings[i1].getName(), ridings[i1])
		}
		return map
	}

	/**
	 * ridingAt finds whichever riding a schedule (primary or secondary entry list) says should be
	 * featured at a given time - the latest entry whose time has already passed.
	 *
	 * @param {Array} entries schedule.primary or schedule.secondary
	 * @param {float} time current simulation time
	 * @param {Map} ridingsByNameMap result of Scheduler.ridingsByName
	 *
	 * @return {Riding|null} the riding scheduled to be featured, or null if none is due yet
	 */
	static ridingAt(entries, time, ridingsByNameMap)
	{
		var name = null
		for(var i1 = 0; i1 < entries.length; i1++)
		{
			if(entries[i1].time <= time)
			{
				name = entries[i1].ridingName
			}
			else
			{
				break
			}
		}

		if(name === null)
		{
			return null
		}

		return ridingsByNameMap.get(name) || null
	}

	/**
	 * #endTime finds the latest moment any riding finishes counting, so the dry run/compile knows
	 * when to stop stepping forward.
	 *
	 * @param {Array} ridings array of Riding
	 *
	 * @return {float}
	 */
	static #endTime(ridings)
	{
		var max = 0
		for(var i1 = 0; i1 < ridings.length; i1++)
		{
			if(ridings[i1].getEndTime() > max)
			{
				max = ridings[i1].getEndTime()
			}
		}
		return max
	}
}
