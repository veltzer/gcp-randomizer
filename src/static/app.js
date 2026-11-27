"use strict";

// The server says every time in UTC, since it cannot know the reader's time
// zone. Say each one (<time datetime="...">) in the reader's own locale and
// time zone instead, as their browser knows them; the UTC wording the server
// sent stays on the element as its tooltip.
function localizeTimes() {
	const format = new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" });
	const zone = format.resolvedOptions().timeZone;
	for (const time of document.querySelectorAll("time[datetime]")) {
		const when = new Date(time.dateTime);
		if (Number.isNaN(when.getTime())) {
			continue;
		}
		time.title = time.textContent;
		time.textContent = zone ? `${format.format(when)} (${zone})` : format.format(when);
	}
}

localizeTimes();
