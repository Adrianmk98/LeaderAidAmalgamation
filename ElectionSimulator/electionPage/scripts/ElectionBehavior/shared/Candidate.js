/**
 * Candidate stores Candidate info
 */
class Candidate
{
	#partyId;
	#name;
	#faceSteal;
	#voteCount = [];
	votes = 0;

	/**
	 * constructor assigns and validates new candidate values
	 *
	 * @param {Array} arguments[0] array of all values within riding.csv
	 *
	 * @param {string} arguments[0] the party Id that the candidate belongs to
	 * @param {string} arguments[1] the name of the candidate
	 * @param {string} arguments[2] the image name of the candidates facesteal
	 * @param {Array} arguments[3] Array of votes received
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
	}

	/**
	 * private #constructor1 assigns and validates new candidate values
	 *
	 * @param {Array} line array of all values with riding.csv
	 *
	 * @param {IlligalArguments} throws if the wrong data type is inserted
	 */
	#constructor1(line)
	{
		if(typeof line[0] === "string")
		{
			this.#partyId = line[0]	
		}
		else
		{
			throw "IlligalArguments"
		}

		if(typeof line[1] === "string")
		{
			this.#faceSteal = line[1]
		}
		else
		{
			throw "IlligalArguments"
		}

		if(typeof line[2] === "string")
		{
			this.#name = line[2]
		}
		else
		{
			throw "IlligalArguments"
		}
		
		for(var i1 = 3; i1 < line.length; i1++)
		{
			if(/^\d+$/.test(line[i1]))
			{
				this.#voteCount.push(parseInt(line[i1]))
			}
			else
			{
				break;
			}
		}
	}

	/**
	 * private #constructor1 assigns and validates new candidate values
	 *
	 * @param {string} partyId the party Id that the candidate belongs to
	 * @param {string} name the name of the candidate
	 * @param {string} faceSteal the image name of the candidates facesteal
	 * @param {Array} voteCount Array of votes received
	 *
	 * @param {IlligalArguments} throws if the wrong data type is inserted
	 */

	#constructor2(partyId, name, faceSteal, voteCount)
	{
		if(typeof partyId === "string")
		{
			this.#partyId = partyId	
		}
		else
		{
			throw "IlligalArguments"
		}

		if(typeof faceSteal === "string")
		{
			this.#faceSteal = faceSteal
		}
		else
		{
			throw "IlligalArguments"
		}

		if(typeof name === "string")
		{
			this.#name = name
		}
		else
		{
			throw "IlligalArguments"
		}
		
		for(var i1 = 3; i1 < voteCount.length; i1++)
		{
			if(/^\d+$/.test(voteCount[i1]))
			{
				this.#voteCount.push(parseInt(voteCount[i1]))
			}
			else
			{
				throw "IlligalArguments"
			}
		}	
	}

	/**
	 * getParty returns the value of the partyId
	 *
	 * @return {String} partyId
	 */
	getParty()
	{
		return this.#partyId
	}

	/**
	 * getName returns the value of the candidate name
	 *
	 * @return {String} name of the candidate
	 */
	getName()
	{
		return this.#name
	}

	/**
	 * getFaceSteal returns the value of the candidate faceSteal file name
	 *
	 * @return {String} file name of faceSteal of candidate
	 */
	getFaceSteal()
	{
		return this.#faceSteal;
	}

	/**
	 * getVoteCount returns the vote count
	 *
	 * @param {float} arguments[0] time value that is between two steps
	 *
	 * @param {integer} arguments[0] step value at given point
	 *
	 * @return {String} file name of faceSteal of candidate
	 *
	 * @throw {IlligalArguments} throws when the wrong number of arguments are given or arguments are not numbers
	 */
	getVoteCount()
	{
		if (arguments.length === 0)
		{
			return this.#getVoteCount1()
		}
		else if(arguments.length === 1)
		{
			if(!isNaN(arguments[0]) && typeof arguments[0] === "number")
			{
				this.votes = this.#getVoteCount2(arguments[0])
				return this.votes
			}
		}

		throw "IlligalArguments"
	}

	/**
	 * getVoteCount1 returns the vote count array
	 *
	 * @return {Array} voteCount array
	 */
	#getVoteCount1()
	{
		return this.#voteCount;
	}

	/**
	 * #getVoteCount2 returns the interpolated voteCount between two voteSteps
	 *
	 * @param {float} time value of the interpolated values
	 *
	 * @return {int} vote count 
	 *
	 * @throws {outOfRangeError} throws when time paramater is greater than the voteCount array or less than 0
	 *
	 * @throws {outOfRangeError} throws when time paramater is greater than the voteCount array or less than 0
	 */
	#getVoteCount2(time)
	{
		var y1 = Math.floor(time)
		var y2 = Math.ceil(time)
		var x = time % 1;

		if(y1 < 0)
		{
			return 0;
		}

		if(y2 >= this.#voteCount.length)
		{
			return this.#voteCount[this.#voteCount.length - 1]
		}

		return Math.round(this.#voteCount[y1] + x * (this.#voteCount[y2] - this.#voteCount[y1]))
	}

	/**
	 * #getVoteCount3 returns the vote count at a given step
	 *
	 * @param {float} time value of the interpolated values
	 *
	 * @return {int} vote count 
	 */
	#getVoteCount3(time)
	{
		if(time < 0 || this.#voteCount.length <= time)
		{
			throw "outOfRangeError"
		}

		return this.#voteCount[time]
	}


}