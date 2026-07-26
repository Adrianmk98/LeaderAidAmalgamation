/**
 * RidingPools stores ridings that are queued and activley being displayed
 */
class RidingPools
{
	queue = []
	active = []
	selected = null;
	max;

	/**
	 * constructor sets up RiddingPools object
	 *
	 * @param {integer} max is the max number of ridings in the active pool
	 * @param {Array} ridings is an array of Riding objects that are inserted in a queue
	 */
	constructor(max, ridings)
	{
		this.max = max

		for(var i1 = 0; i1 < ridings.length; i1++)
		{
			this.queue.push(ridings[i1])
		}

		this.queue.sort((a, b) => 
		{
			return a.getStartTime() - b.getStartTime();
		});

	
		this.active.push(this.queue.splice(0,1)[0])
	}

	/**
	 * updatePool updates queue and active arrays based on time values
	 *
	 * @param {int} time is number value used to update queue and active
	 */
	updatePool(time)
	{
		var tmp;

		for(var i1 = this.queue.length - 1; i1 >= 0; i1--)
		{
			if(time >= this.queue[i1].getStartTime())
			{
				tmp = this.queue[i1]

				this.active.push(tmp)

				this.queue.splice(i1, 1)
			}
		}

		if(!isNaN(this.max))
		{
			var i1 = 0;
			while (this.active.length > this.max && i1 < this.active.length)
			{
				if(this.active[i1].countingCheck(time))
				{
					this.active.splice(i1, 1)
				}
				i1++
			}
		}
	}

	/**
	 * selectActivity picks a random riding in the active pool
	 *
	 * @return {Riding} the new selected riding is returned
	 */
	selectActive()
	{
		if(this.active.length === 0)
		{
			this.selected = null
		}
		else
		{
			this.selected = this.active[Math.floor(Math.random() * this.active.length)]
		}
		return this.selected
	}
}