//inital settings
size = 2;
duration = 10;//seconds
suffix = "jpg"

//internal variables
current = 0;
next = 1;

//background start values
var scale = 1;
var position = {x: 0, y: 0}
var transformDuration = 1;

$("#background #currentBackgroundImage").css("transition-duration",(duration*0.25)+"s")

function changeBackground(d)
{
	if(current + 1 > size)
	{
		current = 0
	}
	else
	{
		current++;
	}

	if(next + 1 > size)
	{
		next = 0
	}
	else
	{
		next++;
	}
	
	/*
	start -(4s)-> start animation -(1s)-> end animation -(1s)-> new back
	 ^_____________________________________________________________| 
	 start
	 	- current opacity 1 
	 start animation
	 	- applies transition class
	 	- begins to change opacity 0
 	 end animation
 	 	- gets rid of transition class
 	 	-
	*/
	
	//start
	setTimeout
	(
		function()
		{	
			//start animation
			$("#currentBackgroundImage").addClass("transition");
			$("#currentBackgroundImage").css("opacity",0);

			setTimeout
			(
				function()
				{
					//end animation
					$("#currentBackgroundImage").attr("src","backgrounds\\"+current+"."+suffix);
					setTimeout
					(
						function()
						{
							//new back
							$("#currentBackgroundImage").css("opacity",1);
							$("#currentBackgroundImage").removeClass("transition")
							
							
							setTimeout
							(
								function()
								{
									$("#nextBackgroundImage").attr("src","backgrounds\\"+next+"."+suffix)	
									changeBackground(duration)
								}
								,
								d * 1000 * 0.25
							)
							
						},
						d * 1000 * 0.1
					)
				},
				d * 1000 * 0.25
			)
		},
		d * 1000 * 0.75
	)
}

//transitionDuration updates transition-duration of the background image
function transitionDuration(d)
{
	$("#background").css("transition-duration", d+"s")
	transformDuration = Math.random() * 10 + 5
	setTimeout
	(
		function()
		{
			transitionDuration(transformDuration)
		},
		d * 1000
	)
}

//backgroundTransform updates the scale and translation of the background image
function backgroundTransform(d)
{
	scale = Math.random() / 4 + 1

	position.x = Math.random() * -29.4117647059
	position.y = Math.random() * (window.innerHeight * -0.15) / window.innerHeight * 100

	$("#background").css("transform", "scale("+scale+") translate("+position.x+"%,"+position.y+"%)")

	setTimeout
	(
		function()
		{
			backgroundTransform(transformDuration + 1)
		},
		d * 1000
	)
}

changeBackground(transformDuration);
backgroundTransform(transformDuration)
transitionDuration(transformDuration)