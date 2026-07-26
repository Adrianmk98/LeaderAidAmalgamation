/**
 * Listener stores functions that are called when certian conditions are met
 */
class Listener
{
	#successAction;
	#failureAction;

	/**
	 * setOnSuccess sets successAction
	 * 
	 * @param {function} action funtion that runs on onSuccess
	 *
	 * @return {Listener} Listener object that just used this method
	 */
	setOnSuccess(action)
	{
		this.#successAction = action;

		return this;
	}

	/**
	 * setOnFailure sets successAction
	 * 
	 * @param {function} action funtion that runs on onFailure
	 *
	 * @return {Listener} Listener object that just used this method
	 */
	setOnFailure(action)
	{
		this.#failureAction = action;

		return this;
	}

	/**
	 * onSuccess runs successAction
	 *
	 * @param {JSon object} data is paramater used in successAction function 
	 *
	 * @return {Listener} Listener object that just used this method
	 */
	onSuccess(data)
	{
		this.#successAction(data);

		return this
	}


	/**
	 * onFailure runs failureAction
	 *
	 * @return {Listener} Listener object that just used this method
	 */
	onFailure()
	{
		this.#failureAction();

		return this
	}
}