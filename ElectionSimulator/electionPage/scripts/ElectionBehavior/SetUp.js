/**
 * SetUp class addresses with the functionality in setting up the election page
 */
class SetUp
{
	partyFeild;
	#partyListener;

	ridingFeild;
	#ridingListener;

	messageFeild;

	primaryTimeFeild = {val:null, unit:null}
	secondaryTimeFeild = {val:null, unit:null}

	iterator;
	static #iteratorPointer;

	/**
	 * constructor assigns values of instances and preps listeners
	 */
	constructor()
	{
		this.#intiateIterator()

		this.partyFeild = $("input#partySettings")[0]
		this.#partyListener = new Listener();

		this.primaryTimeFeild.val = $("input#primary")
		this.primaryTimeFeild.unit = $("select#primary")

		this.secondaryTimeFeild.val = $("input#secondary")
		this.secondaryTimeFeild.unit = $("select#secondary")

		this.#partyListener.setOnSuccess
		(
			function(data)
			{
				for(var i1 = 0; i1 < data.length - 1; i1++)
				{
					Main.addParties(new Party(data[i1]))
				}
				console.log(Main.parties)
				console.log(SetUp.#iteratorPointer.next())
			}
		).setOnFailure
		(
			function()
			{
				console.log("Failure")
			}
		)


		this.ridingFeild = $("input#ridingSettings")[0]
		this.#ridingListener = new Listener();

		this.#ridingListener.setOnSuccess
		(
			function(data)
			{
				for(var i1 = 0; i1 < data.length - 1; i1++)
				{
					try
					{
						if(isNaN(parseFloat(data[i1][0])))
						{
							Main.getRiding(Main.ridingCount() - 1).addCandidate(data[i1])
						}
						else
						{
							Main.addRiding(new Riding(data[i1]))
						}
					}
					catch(ex)
					{
						console.log(ex)
					}
					
					//Main.ridings.push(new Riding(data[i1]))
				}
				console.log(Main.ridings)
				console.log(SetUp.#iteratorPointer.next())
			}
		).setOnFailure
		(
			function()
			{
				console.log("Failure")
			}
		)

		this.messageFeild = $("#setup > #message")
	}

	/*
	 * run method gathers inputed settings into one json object
	 *
	 * @return {Object} json object of parties, ridings and success condition of the method
	 */
	* #run()
	{
		try
		{
			CSVParser.csvToArray
			(
				this.partyFeild.files[0],
				this.#partyListener
			)
			yield

			CSVParser.csvToArray
			(
				this.ridingFeild.files[0],
				this.#ridingListener
			)
			yield

			Main.setPrimaryDuration(this.#calcTime(this.primaryTimeFeild.val.val(),this.primaryTimeFeild.unit.val()))
			Main.setSecondaryDuration(this.#calcTime(this.secondaryTimeFeild.val.val(),this.secondaryTimeFeild.unit.val()))

			this.#startCountDown(10)

			console.log(returnVal)
			
			return returnVal;
		}
		catch(exception)
		{
			console.log(exception)
			this.#sendMessage(exception.toString())
			this.#intiateIterator()
		}
	}

	/**
	 * startCountDown is a recursive method to count down before the election page is actived
	 *
	 * @param {Number} count is an int of the number seconds left before the page starts
	 */
	#startCountDown(count)
	{
		if(count == 5)
		{
			$("#setup").css("display","none")
			Main.initialize()
		}
		else if(count == 0)
		{
			Main.start()
			return ;
		}
		this.#sendMessage("Live Stream Starting in : " + count)
		setTimeout(this.#startCountDown.bind(this, count - 1), 1000)
	}

	/**
	 * feildCheck checks if all settings are set with a valid value
	 * 
	 * @return {boolean} boolean whether all feilds are valid
	 */
	#feildCheck()
	{
		return this.#fileCheck(this.partyFeild.files) && this.#fileCheck(this.ridingFeild.files);
	}

	/**

	 * fileCheck determines if a file feild is set in a useable manner
	 *
	 * @param {Object} files is files instance from file input feild
	 *
	 * @return {boolean} boolean if the file is a csv
	 */
	#fileCheck(files)
	{
		if(files.length != 1)
		{
			return false;
		}

		name = files[0].name.toLowerCase();

		return name.substr(name.length - 3, 3) == "csv"
	}

	/**
	 * sendMessage updates message box
	 *
	 * @param {string} messageStr string value of message that will be displayed
	 */
	#sendMessage(messageStr)
	{
		this.messageFeild.addClass("alert")
		this.messageFeild.text(messageStr)

		setTimeout(this.#hideMessage.bind(this), 10*1000)
	}

	/**
	 * hideMessage hides the message box after being displayed
	 */
	#hideMessage()
	{
		this.messageFeild.removeClass("alert")
	}

	/**
	 * calcTime converts a number and unit into sec
	 *
	 * @param {integer} time is a time value
	 * @param {stirng} unit is the unit of time
	 *
	 * @throws {IlligalArguments} if paramaters are not in the proper data type
	 */
	#calcTime(time, unit)
	{
		if(!(/^\d+$/.test(time)))
		{
			throw new Exception("IlligalArguments", "time must be int")
		}
		switch(unit)
		{
			case "sec":
				return time
			case "min":
				return time * 60
			default:
				throw new Exception("IlligalArguments", "Invalid unit. unit must be 'sec' or 'min'")
		}
	}

	/**
	 * intiateIterator sets up iterator generator
	 */
	#intiateIterator()
	{
		this.iterator = this.#run()
		SetUp.#iteratorPointer = this.iterator
		$("button").click(this.iterator.next.bind(this.iterator))

	}
}

a = new SetUp();