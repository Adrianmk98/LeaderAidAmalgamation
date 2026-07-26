class Main
{
	static #parties = {}
	static #ridings = []

	static #primaryDuration = 0;
	static #secondaryDuration = 0;

	static #primaryRidingPool;
	static #secondaryRidingPool;

	static #active = true;
	static #time = 0;

	static #primaryPolling = new PrimaryPolling();
	static #secondaryPolling = new SecondaryPolling();
	static #seatCount = new SeatCount();
	static #majorityMeter = new MajorityMeter();

	// Finalized featured-riding schedule from Scheduler.build/ControlPanel (null until the
	// moderator confirms it on the Control Panel) - see Scheduler.js for why this replaces the
	// live RidingPools.selectActive() random draw.
	static #schedule = null;
	static #ridingsByName = new Map();
	static #primarySelectedName = null;
	static #secondarySelectedName = null;

	/**
	 * sets up the intial structure of the livestream
	 */
	static initialize()
	{
		console.log("started")

		Main.#primaryRidingPool = new RidingPools(Scheduler.PRIMARY_POOL_MAX, Main.#ridings)
		Main.#secondaryRidingPool = new RidingPools(Scheduler.SECONDARY_POOL_MAX, Main.#ridings)
		Main.#ridingsByName = Scheduler.ridingsByName(Main.#ridings)

		Main.#active = true;

		Main.#primaryRidingPool.updatePool(Main.#time)
		Main.#secondaryRidingPool.updatePool(Main.#time)

		Main.#seatCount.draw(Object.values(Main.#parties))
		Main.#majorityMeter.draw(Object.keys(Main.#parties), Main.#ridings.length)

		Main.#update()

		Main.pause()
	}

	/**
	 * start method starts the livestream
	 */
	static start()
	{
		Main.play()
	}

	/**
	 * setSchedule installs the finalized (dry-run, possibly moderator-edited) featured-riding
	 * schedule produced by Scheduler.build/ControlPanel, so the live broadcast replays it instead
	 * of drawing a fresh random riding each tick.
	 *
	 * @param {Object} schedule {primary: [{time, ridingName}], secondary: [{time, ridingName}]}
	 */
	static setSchedule(schedule)
	{
		Main.#schedule = schedule
	}

	/**
	 * getSchedule returns the currently installed schedule (or null if none has been confirmed
	 * yet).
	 *
	 * @return {Object|null}
	 */
	static getSchedule()
	{
		return Main.#schedule
	}

	/**
	 * getParties returns the parties map (key -> Party).
	 *
	 * @return {Object}
	 */
	static getParties()
	{
		return Main.#parties
	}

	/**
	 * getRidings returns the full ridings array.
	 *
	 * @return {Array}
	 */
	static getRidings()
	{
		return Main.#ridings
	}

	/**
	 * getPrimaryDuration returns the configured primary panel switch duration, in seconds.
	 *
	 * @return {float}
	 */
	static getPrimaryDuration()
	{
		return Main.#primaryDuration
	}

	/**
	 * getSecondaryDuration returns the configured secondary panel switch duration, in seconds.
	 *
	 * @return {float}
	 */
	static getSecondaryDuration()
	{
		return Main.#secondaryDuration
	}

	/**
	 * update method handles the updating of riding veiws
	 */
	static #update()
	{
		$("div#reportingPolls").html(
			"Polls Reporting "
			+ Main.#secondaryRidingPool.active.length
			+ "/"
			+ (Main.#secondaryRidingPool.queue.length+Main.#secondaryRidingPool.active.length)
		)
		if(Main.#active)
		{
			Main.#primaryRidingPool.updatePool(Main.#time)
			Main.#secondaryRidingPool.updatePool(Main.#time)

			if(Main.#schedule !== null)
			{
				Main.#updateFromSchedule()
			}
			else
			{
				Main.#updateLiveRandom()
			}

			Main.#seatCount.update(Main.#ridings, Main.#time)
			Main.#majorityMeter.update(Main.#ridings, Main.#time)

			var parties = Object.values(Main.#parties)
			for(var i1 = 0; i1 < parties.length; i1++)
			{
				parties[i1].updateElements()
			}

			Main.#time++;
		}

		setTimeout(Main.#update, 1000)
	}

	/**
	 * #updateFromSchedule features whichever riding the finalized schedule says is due for the
	 * current tick, on both the primary and secondary panels.
	 */
	static #updateFromSchedule()
	{
		var primaryRiding = Scheduler.ridingAt(Main.#schedule.primary, Main.#time, Main.#ridingsByName)
		if(primaryRiding !== null)
		{
			if(primaryRiding.getName() !== Main.#primarySelectedName)
			{
				Main.#primarySelectedName = primaryRiding.getName()
				Main.#primaryPolling.draw(primaryRiding, Main.#parties, Main.#time)
			}
			else
			{
				Main.#primaryPolling.update(primaryRiding, Main.#parties, Main.#time)
			}
		}

		var secondaryRiding = Scheduler.ridingAt(Main.#schedule.secondary, Main.#time, Main.#ridingsByName)
		if(secondaryRiding !== null)
		{
			if(secondaryRiding.getName() !== Main.#secondarySelectedName)
			{
				Main.#secondarySelectedName = secondaryRiding.getName()
				Main.#secondaryPolling.draw(secondaryRiding, Main.#parties, Main.#time)
			}
			else
			{
				Main.#secondaryPolling.update(secondaryRiding, Main.#parties, Main.#time)
			}
		}
	}

	/**
	 * #updateLiveRandom is the original behaviour (kept as a fallback for anyone driving Main
	 * directly without ever going through the Control Panel/Scheduler): picks a fresh random
	 * riding live, each time a duration boundary is hit.
	 */
	static #updateLiveRandom()
	{
		if(Main.#primaryRidingPool.active.length > 0)
		{
			if(Main.#time % Main.#primaryDuration === 0)
			{
				Main.#primaryRidingPool.selectActive()
				Main.#primaryPolling.draw(Main.#primaryRidingPool.selected, Main.#parties, Main.#time)
			}
			else
			{
				if(Main.#primaryRidingPool.selected !== null)
				{
					Main.#primaryPolling.update(Main.#primaryRidingPool.selected, Main.#parties, Main.#time)
				}
			}
		}
		if(Main.#secondaryRidingPool.active.length > 0)
		{
			if(Main.#time % Main.#secondaryDuration === 0)
			{
				Main.#secondaryRidingPool.selectActive()
				Main.#secondaryPolling.draw(Main.#secondaryRidingPool.selected, Main.#parties, Main.#time)
			}
			else
			{
				if(Main.#secondaryRidingPool.selected !== null)
				{
					Main.#secondaryPolling.update(Main.#secondaryRidingPool.selected, Main.#parties, Main.#time)
				}
			}
		}
	}

	/**
	 * togglePause plays/pauses the livestream based on whether livestream is active
	 */
	static togglePause()
	{
		Main.#active = !Main.#active
	}

	/**
	 * play plays the livestream
	 */
	static play()
	{
		Main.#active = true
	}

	/**
	 * pause pauses the livestream
	 */
	static pause()
	{
		Main.#active = false;
	}

	/**
	 * addParties appends a new party into parties array
	 *
	 * @param {param} party that will be appended to parties
	 *
	 * @throw {IlligalArguments} throws when paramaters are not party
	 */
	static addParties(party)
	{
		if(typeof party === "object" && party.constructor.name === Party.name)
		{
			Main.#parties[party.getKey()]=party
		}
		else
		{
			throw "IlligalArguments"
		}
	}

	/**
	 * addRiding appends a new riding into ridings array
	 *
	 * @param {param} riding that will be appended to ridings
	 *
	 * @throw {IlligalArguments} throws when paramaters are not riding
	 */
	static addRiding(riding)
	{
		if(typeof riding === "object" && riding.constructor.name === Riding.name)
		{
			Main.#ridings.push(riding)
		}
		else
		{
			throw "IlligalArguments"
		}
	}

	/**
	 * getRiding gets the riding at specfic index
	 *
	 * @param {param} index is number 
	 *
	 * @returns {Riding} riding at index
	 */
	static getRiding(index)
	{
		return Main.#ridings[index]
	}

	/**
	 * ridingCount gets the number of ridings
	 *
	 * @return {integer} number of ridings
	 */
	static ridingCount()
	{
		return Main.#ridings.length
	}

	/**
	 * setPrimaryDuration sets the number of seconds the primary riding vissible before transition to another ridding 
	 *
	 * @param {param} duration that will be visible before transition to another riding
	 *
	 * @throw {IlligalArguments} throws when paramaters are not int
	 */
	static setPrimaryDuration(duration)
	{
		if(/^\d+$/.test(duration))
		{
			Main.#primaryDuration = duration
		}
		else
		{
			throw "IlligalArguments"
		}
	}

	/**
	 * setSecondaryDuration sets the number of seconds the secondary riding vissible before transition to another ridding 
	 *
	 * @param {param} duration that will be visible before transition to another riding
	 *
	 * @throw {IlligalArguments} throws when paramaters are not int
	 */
	static setSecondaryDuration(duration)
	{
		if(/^\d+$/.test(duration))
		{
			Main.#secondaryDuration = duration
		}
		else
		{
			throw "IlligalArguments"
		}
	}
}