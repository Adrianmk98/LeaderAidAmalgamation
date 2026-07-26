# Election Livestream Page

## Description
The Election Livestream page is a web app that simulates election livestream. The web app is modeled of the Global News Decision Canada.
Reference | Election Livestream Web App
------------ | -------------
![image](https://user-images.githubusercontent.com/34819460/127887846-1e2236d3-ba20-4954-9cc4-02200137a14e.png) | ![image](https://user-images.githubusercontent.com/34819460/127887356-23135b77-5ea6-412a-a7f8-6ab226d9cea7.png)

![image](https://user-images.githubusercontent.com/34819460/127913792-c200b557-b154-4ddc-96b6-d71a36ee6e78.png)

It's a plain static page - jQuery plus a set of vanilla JS classes, no build step, no server required for the core livestream (CSV parsing runs entirely in the browser via `FileReader`). The one feature that *does* need a server is video export - see [Compile Video](#compile-video) below.

## Quick Start (Demo)

A ready-to-go sample dataset lives in [`demo/`](demo/): `parties-demo.csv` and `ridings-demo.csv` (4 parties, 6 ridings with a mix of landslides, a surge win, a third-party breakthrough, and a razor-thin nail-biter - good material for trying out the Control Panel's reordering and stats).

To run it:
1. Double-click **`run-demo.bat`**. It starts a local server (`python -m http.server 8781`) in its own window and opens the simulator in your default browser.
2. On the setup screen, upload:
   - Party Data: `demo/parties-demo.csv`
   - Riding Data: `demo/ridings-demo.csv`
3. Set Primary/Secondary to `5` sec each for a quick run-through, then press **RUN**.

Use a server (not just double-clicking `index.html`) whenever you want to use **Compile Video** - browsers block `fetch()` of local files under a bare `file://` page, which that feature needs. Everything else (setup, Control Panel, live broadcast) works fine either way.

## SetUp
### Download File and Open Index.html
![image](https://user-images.githubusercontent.com/34819460/127898993-df2601af-5894-4ec0-ad21-08e2ac45846b.png)
### Fillout settings
#### Insert election csv
![image](https://user-images.githubusercontent.com/34819460/127910954-e148f8c4-6da4-4b62-990c-2bb0768b81e6.png)
A party CSV should be inserted into the party data field
A riding CSV should be inserted into the riding data field
#### Set up
Once, the files are inserted, the rotation timers should be set for the primary and secondary polling areas.
![image](https://user-images.githubusercontent.com/34819460/127911349-1e467455-c7be-484c-ba3a-0605b80ac087.png)

## Control Panel
Pressing the setup button doesn't go straight to a live countdown - it opens the **Control Panel** first, so a moderator can see how the results will play out and adjust the pacing/drama before anyone's watching. Nothing here is time-pressured; the whole broadcast is simulated once up front so every view below reflects the exact same underlying vote data.

- **Riding Stats** - a sortable table summarizing every riding: `Final Margin`, `Closest Margin` measured from a configurable step onward (e.g. "closest it gets after step 5"), and `Lead Changes` (how many times the projected winner flips over the course of the count). Click a column header to sort by it, click a row to load that riding into the step editor below - this is the fastest way to find your nail-biters and your landslides.
- **Seat Projection** - a live line chart of each party's projected seat count over the length of the broadcast, redrawn any time you edit or reroll a riding's data.
- **Running Order** - the Primary and Secondary panel schedules, in time order. Click a riding's name (in either list, or in the stats table, or in the step editor's own riding chips) to load it into the step editor. Use the ▲ / ▼ buttons to swap which riding fills a given time slot - reordering only changes *which riding airs when*, not the underlying results. **Reroll Random Order** throws out the current running order and draws a fresh random one.
- **Edit Riding Steps** - once a riding is selected (via a running-order click, a stats-table click, or one of the small riding chips), its full candidates x polling-steps table is shown here. Every step is a plain editable number - change any value directly, or use **Reroll Selected** (a `from`/`to` step range) or **Reroll All** to regenerate a run of steps with a random, still-monotonically-increasing vote progression that reconnects smoothly with whatever you didn't touch.
- **Compile Video** - see [below](#compile-video). Available here so you can export a recording without ever having to sit through the live broadcast.
- **Confirm & Go Live** - locks in the schedule and running order exactly as edited, and starts the countdown into the live broadcast.

## Press the start button
Once the start button is pressed a timer will count down till the beginning of the election live stream
![image](https://user-images.githubusercontent.com/34819460/127911516-08f693fa-e778-4245-b48a-d541bb76a18f.png)

## Compile Video
"Compile Video" (on the Control Panel, and again on the live broadcast screen) renders the entire broadcast straight to a downloadable `.webm` file. It isn't a screen recording - since the whole schedule and every riding's vote data is already fully known, it renders each tick directly and encodes it, so it doesn't take as long as the real broadcast would. It needs:
- A page served over `http://`/`https://` (see [Quick Start](#quick-start-demo)) rather than opened directly as a file, since it fetches the stylesheet/images to render each frame.
- A Chromium-based browser (Chrome/Edge) - it depends on the browser's built-in WebCodecs video encoder, which isn't available everywhere yet.

## Input CSV files

### Parties.csv
The Party csv stores the infomration about each party running candidate in a election
#### Template
KEY | SHORT NAME | LONG NAMES | Colour
#### Example
![image](https://user-images.githubusercontent.com/34819460/127912237-3500b399-4a56-4a65-ab27-9f86fb0ab00b.png)

### Riding.csv
The Riding CSV stores the information about each riding and candidate in the election.
#### Template
Seconds Before Start Time |	Second Between Polling CheckPoints |	Riding Population Size |	Riding Name		
Party Key 1 |	Face Steal File | Party	Name |	#num1 |	#num2 |	#num3 |	#num4 |	#num5 |	#num6 |	#num7 |	#num8	

#### Example
![image](https://user-images.githubusercontent.com/34819460/127912625-44fe9297-9029-40e6-bcd4-ded9b1c5d1cf.png)

Note: the `#num1..#num8` columns don't have to be final before you upload - every one of them can still be hand-edited or randomly rerolled (in part or in full) from the Control Panel's step editor once the file is loaded.
