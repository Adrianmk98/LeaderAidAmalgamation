/**
 * VideoCompiler renders the entire finalized broadcast straight to a downloadable .webm file by
 * driving the same DOM the live broadcast uses, tick by tick, and encoding each tick as one video
 * frame - not a live screen-recording. Since every visual and vote total is already fully known
 * once the Control Panel's schedule is locked in (see Scheduler.js), there is nothing to wait for
 * in real time: this runs as fast as the browser can render + encode each frame.
 *
 * Uses Mediabunny (https://mediabunny.dev), loaded here as an ES module straight from a CDN, for
 * WebM muxing on top of the browser's native WebCodecs VideoEncoder - there is no bundler/build
 * step anywhere in this project, so this file is loaded via <script type="module"> instead of a
 * classic <script>, and re-exposes the class as `window.VideoCompiler` so the rest of the
 * (non-module) codebase can call it the same way as everything else.
 *
 * NOTE: this integration is based on Mediabunny's published docs and could not be exercised in a
 * live browser from the environment this was written in - if the CDN import or API surface has
 * moved on, the fix is isolated to the `import(...)` line and the Mediabunny.* calls below.
 */

let Mediabunny = null
try
{
	Mediabunny = await import("https://cdn.jsdelivr.net/npm/mediabunny/+esm")
}
catch(loadError)
{
	console.error("VideoCompiler: failed to load Mediabunny from CDN", loadError)
}

class VideoCompiler
{
	static #cssTextPromise = null
	static #imageCache = new Map()

	/**
	 * compile renders the full schedule to a .webm file and triggers a download. Safe to call
	 * either from the Control Panel (before going live) or from the live broadcast screen (to
	 * export a recording of what already aired) - either way it renders from the data, not from
	 * whatever is currently on screen.
	 *
	 * @param {Object} parties key -> Party
	 * @param {Array} ridings array of Riding
	 * @param {Object} schedule {primary, secondary, endTime} from Scheduler.build
	 * @param {jQuery} statusEl element to show progress text in (optional)
	 */
	static async compile(parties, ridings, schedule, statusEl)
	{
		if(Mediabunny === null)
		{
			if(statusEl)
			{
				statusEl.text("Video export unavailable: could not load the Mediabunny video library. Check your internet connection and try again.")
			}
			return
		}

		if(typeof Main !== "undefined")
		{
			Main.pause()
		}

		var node = document.getElementById("ridingResults")
		var width = window.innerWidth
		var height = window.innerHeight

		var canvas = document.createElement("canvas")
		canvas.width = width
		canvas.height = height

		var output = new Mediabunny.Output
		({
			format: new Mediabunny.WebMOutputFormat(),
			target: new Mediabunny.BufferTarget(),
		})

		var videoSource = new Mediabunny.CanvasSource(canvas,
		{
			codec: "vp9",
			bitrate: Mediabunny.QUALITY_HIGH !== undefined ? Mediabunny.QUALITY_HIGH : 1e6,
		})

		output.addVideoTrack(videoSource)
		await output.start()

		var seatCount = new SeatCount()
		var majorityMeter = new MajorityMeter()
		var primaryPolling = new PrimaryPolling()
		var secondaryPolling = new SecondaryPolling()

		var partyList = Object.values(parties)

		seatCount.draw(partyList)
		majorityMeter.draw(Object.keys(parties), ridings.length)

		var ridingsByName = Scheduler.ridingsByName(ridings)
		var primarySelectedName = null
		var secondarySelectedName = null

		var cssText = await VideoCompiler.#loadCss()

		for(var time = 0; time <= schedule.endTime; time++)
		{
			var primaryRiding = Scheduler.ridingAt(schedule.primary, time, ridingsByName)
			if(primaryRiding !== null)
			{
				if(primaryRiding.getName() !== primarySelectedName)
				{
					primarySelectedName = primaryRiding.getName()
					primaryPolling.draw(primaryRiding, parties, time)
				}
				else
				{
					primaryPolling.update(primaryRiding, parties, time)
				}
			}

			var secondaryRiding = Scheduler.ridingAt(schedule.secondary, time, ridingsByName)
			if(secondaryRiding !== null)
			{
				if(secondaryRiding.getName() !== secondarySelectedName)
				{
					secondarySelectedName = secondaryRiding.getName()
					secondaryPolling.draw(secondaryRiding, parties, time)
				}
				else
				{
					secondaryPolling.update(secondaryRiding, parties, time)
				}
			}

			seatCount.update(ridings, time)
			majorityMeter.update(ridings, time)

			for(var i1 = 0; i1 < partyList.length; i1++)
			{
				partyList[i1].updateElements()
			}

			await VideoCompiler.#drawFrame(node, canvas, cssText, width, height)
			await videoSource.add(time, 1)

			if(statusEl)
			{
				statusEl.text("Compiling video... " + time + "/" + schedule.endTime + "s")
			}
		}

		await output.finalize()

		var blob = new Blob([output.target.buffer], {type: "video/webm"})
		VideoCompiler.#download(blob, "cmhoc-election-" + Date.now() + ".webm")

		if(statusEl)
		{
			statusEl.text("Video saved.")
		}
	}

	/**
	 * #loadCss fetches the page's stylesheet once so it can be embedded into every captured frame -
	 * a foreignObject-rendered SVG snapshot has no access to the parent document's external
	 * stylesheet, so without this every frame would render unstyled.
	 *
	 * @return {Promise<string>}
	 */
	static #loadCss()
	{
		if(VideoCompiler.#cssTextPromise === null)
		{
			VideoCompiler.#cssTextPromise = fetch("styles/styles.css").then((response) => response.text())
		}
		return VideoCompiler.#cssTextPromise
	}

	/**
	 * #inlineImages rewrites every <img src="..."> in a cloned node to a cached data: URI so the
	 * canvas isn't tainted by loading images inside the SVG foreignObject snapshot.
	 *
	 * @param {Element} clone
	 */
	static async #inlineImages(clone)
	{
		var images = clone.querySelectorAll("img")
		for(var i1 = 0; i1 < images.length; i1++)
		{
			var src = images[i1].getAttribute("src")
			if(!src || src.indexOf("data:") === 0)
			{
				continue
			}

			if(!VideoCompiler.#imageCache.has(src))
			{
				var response = await fetch(src)
				var blob = await response.blob()
				var dataUrl = await new Promise((resolve) =>
				{
					var reader = new FileReader()
					reader.onload = () => resolve(reader.result)
					reader.readAsDataURL(blob)
				})
				VideoCompiler.#imageCache.set(src, dataUrl)
			}

			images[i1].setAttribute("src", VideoCompiler.#imageCache.get(src))
		}
	}

	/**
	 * #drawFrame snapshots the current state of `node` into `canvas` using the SVG foreignObject
	 * DOM serialization technique, so the video always matches exactly what the live broadcast
	 * would show for this tick (same facade rendering code, no second visual implementation).
	 *
	 * @param {Element} node the live #ridingResults element
	 * @param {HTMLCanvasElement} canvas
	 * @param {string} cssText
	 * @param {integer} width
	 * @param {integer} height
	 */
	static async #drawFrame(node, canvas, cssText, width, height)
	{
		var clone = node.cloneNode(true)
		await VideoCompiler.#inlineImages(clone)

		var svgHtml =
			'<svg xmlns="http://www.w3.org/2000/svg" width="' + width + '" height="' + height + '">' +
				'<foreignObject width="100%" height="100%">' +
					'<div xmlns="http://www.w3.org/1999/xhtml" style="width:' + width + 'px;height:' + height + 'px;">' +
						'<style>' + cssText + '</style>' +
						clone.outerHTML +
					'</div>' +
				'</foreignObject>' +
			'</svg>'

		var img = new Image(width, height)
		var url = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svgHtml)

		await new Promise((resolve, reject) =>
		{
			img.onload = resolve
			img.onerror = reject
			img.src = url
		})

		var ctx = canvas.getContext("2d")
		ctx.clearRect(0, 0, width, height)
		ctx.drawImage(img, 0, 0, width, height)
	}

	/**
	 * #download triggers a browser download of a Blob via a temporary hidden link.
	 *
	 * @param {Blob} blob
	 * @param {string} filename
	 */
	static #download(blob, filename)
	{
		var url = URL.createObjectURL(blob)
		var link = document.createElement("a")
		link.href = url
		link.download = filename
		document.body.appendChild(link)
		link.click()
		document.body.removeChild(link)
		URL.revokeObjectURL(url)
	}
}

window.VideoCompiler = VideoCompiler
