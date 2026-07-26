/**
 * Riding class holds riding info and 
 */
class Riding
{
	#endTimeBuffer = 5

	#name;
	#population;
	#startTime;
	#endTime = 0;
	#deltaTime;
	
	#candidates = []

	#winnerCalc;

	votes = 0


	/**
	 * constructor assigns and validates new candidate values
	 * 
	 * @param {Array} arguments[0] array of all values within riding.csv
	 *
	 * @param {String} arguments[0] name of riding
	 * @param {int} arguments[1] population of riding
	 * @param {float} arguments[2] the time in which the riding polling should start counting votes
	 * @param {float} arguments[3] the time between each polling step
	 *
	 * @throw {IlligalArguments} throws if the wrong number of IlligalArguments were given
	 */
	constructor()
	{
		if (arguments.length === 1)
		{
			this.#constructor1(arguments[0]);
		}
		else if(arguments.length === 4)
		{
			this.#constructor2(arguments[0], arguments[1], arguments[2], arguments[3])
		}
		else
		{
			throw "IlligalArguments";
		}

		this.#winnerCalc = new FirstPastThePost()
	}

	/**
	 * constructor1 assigns and validates new candidate values
	 * 
	 * @param {Array} line array of all values within riding.csv
	 *
	 * @throw {IlligalArguments} throws line does not have 4 items
	 */
	#constructor1(line)
	{
		if(line.length < 4)
		{
			throw "IlligalArguments"
		}

		if(!isNaN(parseFloat(line[0])))
		{
			this.#startTime = parseFloat(line[0])
		}
		else
		{
			throw "IlligalArguments"
		}

		if(!isNaN(parseFloat(line[1])))
		{
			this.#deltaTime = parseFloat(line[1])
		}
		else
		{
			throw "IlligalArguments"
		}

		if(/^\d+$/.test(line[2]))
		{
			this.#population = parseInt(line[2])
		}
		else
		{
			throw "IlligalArguments"
		}

		this.#name = line[3]
	}

	/**
	 * constructor2 assigns and validates new candidate values
	 * 
	 * @param {String} name name of riding
	 * @param {int} population population of riding
	 * @param {float} startTime the time in which the riding polling should start counting votes
	 * @param {float} deltaTime the time between each polling step
	 *
	 * @param {IlligalArguments} throws if the wrong data type is inserted
	 */
	#constructor2(name, population, startTime, deltaTime)
	{
		if(typeof name === "string")
		{
			this.#name = name;
		}
		else
		{
			throw "IlligalArguments";
		}

		if(/^\d+$/.test(population.toString()))
		{
			this.#population = population;
		}
		else
		{
			throw "IlligalArguments";
		}

		if(!isNaN(startTime) && typeof startTime === "number")
		{
			this.#startTime = startTime;
			console.log(this.#startTime)
			console.log(startTime)
		}
		else
		{
			throw "IlligalArguments";
		}

		if(!isNaN(deltaTime) && typeof deltaTime === "number")
		{
			this.#deltaTime = deltaTime;
		}
		else
		{
			throw "IlligalArguments";
		}
	}
	
	/**
	 * addCandidate adds a Candidate Object to #candidates array
	 * 
	 * @param {Candidate} candidate object that is added to #candidates array
	 * @param {Array} candidate array from riding.csv
	 */
	addCandidate(candidate)
	{
		if(typeof candidate === "object" && candidate.constructor.name === Party.name)
		{
			this.#candidates.push(candidate)
		}
		else if(Array.isArray(candidate))
		{
			var tmp = new Candidate(candidate)

			this.#candidates.push(tmp)
		}
		else
		{
			throw new Exception("IlligalArguments", "candidate must be an array or canadidate object")
		}

		var maxTime = (this.#candidates[this.#candidates.length - 1] - 1) * this.#deltaTime

		if(maxTime > this.#endTime)
		{
			this.#endTime = maxTime
		}
	}

	/**
	 * getName returns the name of riding
	 *
	 * @return {string} name of the riding
	 */
	getName()
	{
		return this.#name
	}

	/**
	 * getPopulation returns the number of people in a population
	 *
	 * @return {int} name of the riding
	 */
	getPopulation()
	{
		return this.#population
	}
	
	/**
	 * getStartTime returns the start time in seconds since the begining of the liveStream
	 *
	 * @return {float} the counting start time of the riding
	 */
	getStartTime()
	{
		return this.#startTime
	}
	
	/**
	 * getDeltaTime returns the number of seconds between updates
	 *
	 * @return {float} the delta time
	 */
	getDeltaTime()
	{
		return this.#deltaTime
	}
	
	
	/**
	 * getCandidate returns the candidates in the riding
	 *
	 * @return {Array} the candidates in the riding and their votes
	 */
	getCandidateVote(time)
	{
		var candidateVote = []
		this.votes = 0
		for(var i1 = 0; i1 < this.#candidates.length; i1++)
		{
			this.#candidates[i1].getVoteCount((time - this.#startTime)/this.#deltaTime)
			candidateVote.push(this.#candidates[i1])
			this.votes+=this.#candidates[i1].votes
		}

		candidateVote.sort((a, b) => 
		{
			return a.votes - b.votes;
		});

		candidateVote.reverse()
		return candidateVote
	}
	
	/**
	 * countingCheck checks if the riding is still counting
	 *
	 * @param {float} time is the current time stamp
	 *
	 * @return {boolean} a boolean if the riding is still counting
	 */
	countingCheck(time)
	{
		if(isNaN(parseFloat(time.toString())))
		{
			throw new Exception("IlligalArguments", "time must be float")
		}

		return time > this.#endTime + this.#startTime
	}

	/**
	 * getWinner returns the parties that won a seat in the riding
	 *
	 * @return {array} array or parties that won a seat
	 */
	getWinner()
	{
		return this.#winnerCalc.calculate(this.#candidates)
	}

}