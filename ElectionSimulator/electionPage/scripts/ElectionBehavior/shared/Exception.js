class Exception
{
	error;
	message;

	/**
	 * constructor assigns error code and optional message
	 *
	 * @param {string} error name or exception
	 * @param {string} message is string providing additonal information about the exception 
	 *
	 * @throw {Exception} throws when paramaters are strings 
	 */
	constructor(error, message = "")
	{
		if(typeof error === "string")
		{
			this.error = error
		}
		else
		{
			throw new Exception("IlligalArguments", "error must be string");
		}

		if(typeof message === "string")
		{
			this.message = message
		}
		else
		{
			throw new Exception("IlligalArguments", "message must be string");
		}
	}

	/**
	 * toString returns string of exception and message
	 *
	 * @return {string} string of exception and message
	 */
	toString()
	{
		return this.error+" : "+this.message
	}
}