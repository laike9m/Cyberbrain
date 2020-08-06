/*
If you want to modify this file, you may find it hard because the vis-network lib
is not imported directly, so you won't have auto-complete. Due to the limitation
 of vscode,
(https://github.com/microsoft/vscode/issues/72900#issuecomment-487140263)
it's impossible to import a file, as it requires sending http requests.

So I pretty much just rely on my IDE (PyCharm in this case) to provide the
definitions for me. In "Languages & Frameworks > JavaScript > Libraries", you
can add the local vis-network.js file as a library, so that PyCharm recognizes
the vis object, and can provide auto-complete. See
https://i.loli.net/2020/08/05/FBqXQpjk4YVLGRa.png

For other IDEs/editors, I believe it's possible to achieve a similar effect.

I also tried using making this file a ts file but met a few difficulties:
1. The documentation for using TS with vis-network is poor
2. It seems not so easy to use TS without a framework like React/Angular, which
   I'd like to avoid at least for now.
*/

window.addEventListener("message", (event) => {
  console.log(event.data);

  let events = event.data.events;
  let nodes = new vis.DataSet([]);
  for (let identifier in events) {
    if (Object.prototype.hasOwnProperty.call(events, identifier)) {
      for (let event of events[identifier]) {
        nodes.add({
          id: event.uid,
          level: event.lineno,
          label: buildLabelText(event),
        });
      }
    }
  }

  let tracingResult = event.data.tracingResult;
  const edges = new vis.DataSet([]);
  for (let event_uid in tracingResult) {
    if (Object.prototype.hasOwnProperty.call(tracingResult, event_uid)) {
      for (let source_event_uid of tracingResult[event_uid]) {
        edges.add({ from: source_event_uid, to: event_uid });
      }
    }
  }

  const container = document.getElementById("vis");
  const data = {
    nodes: nodes,
    edges: edges,
  };
  const options = {};
  const network = new vis.Network(container, data, options);
});

function buildLabelText(event) {
  return `${event.target}: ${event.type}`;
}
