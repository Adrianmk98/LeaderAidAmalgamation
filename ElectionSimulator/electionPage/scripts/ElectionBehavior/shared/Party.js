/**
 * Party stores infomration relating to a party and updating all elements relating to a certian party
 */
class Party
{
	#colour;
	#name;
	#abrv;//abbreviation
	#key;

	/**
	 * constructor assigns and validates new party values
	 *
	 * @param {Array} arguments[0] array of colour, name and abrv
	 * 
	 * @param {String} arguments[0] hexcode or rgb colour value of party
	 * @param {String} arguments[1] long name of party
	 * @param {String} arguments[2] abbreviation of party
	 * @param {String} arguments[3] party key
	 *
	 * @throw {IlligalArguments} constructor takes either 1 array or 3 string values
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
	 * private constructor1 intiates Party using array
	 *
	 * @param {Array} line array storing colour, name and abrv
	 *
	 * @throw {IlligalArguments} throws when line is not an array
	 */
	#constructor1(line)
	{
		if(!Array.isArray(line))
		{
			throw "IlligalArguments";
		}

		this.#constructor2(line[3], line[2], line[1], line[0])
	}

	/**
	 * private constructor2 intiates Party using array
	 *
	 * @param {String} colour hexcode or rgb colour value of party
	 * @param {string} name long name of party
	 * @param {string} abrv abbreviation of party
	 * @param {String} key party key
	 *
	 * @throw {IlligalArguments} throws when paramaters are not strings
	 */
	#constructor2(colour, name, abrv, key)
	{
		if(typeof colour === 'string')
		{
			this.#colour = colour
		}
		else
		{
			throw "IlligalArguments"
		}

		if(typeof name === "string")
		{
			this.#name = name;
		}
		else
		{
			throw "IlligalArguments"
		}

		if(typeof abrv === "string")
		{
			this.#abrv = abrv;
		}
		else
		{
			throw "IlligalArguments"
		}

		if(typeof key === "string")
		{
			this.#key = key;
		}
		else
		{
			throw "IlligalArguments"
		}
	}

	/**
	 * returns the string for key
	 *
	 * @return {String} key value
	 */
	getKey()
	{
		return this.#key;
	}

	/**
	 * returns the string for name
	 *
	 * @return {String} name value
	 */
	getName()
	{
		return this.#name
	}

	/**
	 * returns the string for party abrevation
	 *
	 * @return {String} party abrevation value
	 */
	getAbrv()
	{
		return this.#abrv
	}
	
	/**
	 * updateElements updates the colour format of all html elements with key id
	 */
	updateElements()
	{
		$("#" + this.#key + " .partyColourBorder, "+"#" + this.#key + ".partyColourBorder").css("border-color", this.#colour)
		$("#" + this.#key + " .partyColour, "+ "#" + this.#key + ".partyColour").css("background-color", this.#colour)
	}
}