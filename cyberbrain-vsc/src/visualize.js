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

let backGroundColor = window
  .getComputedStyle(document.body, null)
  .getPropertyValue("background-color");

const options = {
  nodes: {
    shape: "box",
  },
  edges: {
    smooth: {
      type: "cubicBezier",
      forceDirection: "vertical",
    },
  },
  interaction: {
    dragNodes: false,
    hover: true,
  },
  layout: {
    hierarchical: {
      direction: "UD", // From up to bottom.
    },
  },
  physics: {
    hierarchicalRepulsion: {
      avoidOverlap: 1, // puts the most space around nodes to avoid overlapping.
    },
  },
};

window.addEventListener("message", (event) => {
  if (!event.data.hasOwnProperty("events")) {
    return; // Server ready message.
  }

  console.log(event.data);

  let lines = new Set();
  let events = event.data.events;
  let colorGenerator = new ColorGenerator(Object.keys(events));
  let nodes = new vis.DataSet([]);
  for (let identifier in events) {
    if (Object.prototype.hasOwnProperty.call(events, identifier)) {
      for (let event of events[identifier]) {
        let linenoString = event.lineno.toString();
        if (!lines.has(linenoString)) {
          // Adds a "virtual node" to show line number. This node should precede other nodes
          // on the same level. According to https://github.com/visjs/vis-network/issues/926,
          // the order is not deterministic, but seems it's roughly the same as the insertion
          // order.
          lines.add(linenoString);
          nodes.add({
            title: `Line ${event.lineno}`,
            id: linenoString,
            level: event.lineno,
            label: linenoString,
            borderWidth: 0,
            // Disable physics so the lineno nodes are not pushed away to the left.
            physics: false,
            color: {
              border: backGroundColor,
              background: backGroundColor,
            },
          });
        }
        nodes.add({
          title: getTooltipTextForEventNode(event),
          id: event.uid,
          level: event.lineno,
          label: buildLabelText(event),
          target: event.target,
          // "value" is reserved, use "runtimeValue" instead.
          runtimeValue: event.value,
          color: {
            background: colorGenerator.getColor(event.target),
            hover: {
              // Right now we let color keeps unchanged when hovering. We may slightly
              // change the color to make the node obvious.
              background: colorGenerator.getColor(event.target),
            },
          },
        });
      }
    }
  }

  const edges = new vis.DataSet([]);

  // Add hidden edges so that lineno nodes are placed on the same vertical position.
  lines = Array.from(lines);
  lines.sort();
  for (let i = 0; i < lines.length - 1; i++) {
    edges.add({
      from: lines[i],
      to: lines[i + 1],
      color: {
        color: backGroundColor,
      },
    });
  }

  let tracingResult = event.data.tracingResult;
  for (let event_uid in tracingResult) {
    if (Object.prototype.hasOwnProperty.call(tracingResult, event_uid)) {
      for (let source_event_uid of tracingResult[event_uid]) {
        edges.add({
          from: source_event_uid,
          to: event_uid,
        });
      }
    }
  }

  const container = document.getElementById("vis");
  const data = {
    nodes: nodes,
    edges: edges,
  };
  const network = new vis.Network(container, data, options);
  network.on("hoverNode", function (event) {
    let node = nodes.get(event.node);
    if (!node.hasOwnProperty("target")) {
      return;
    }
    console.log(
      `${node.target}'s value at line ${node.level}: \n ${node.runtimeValue}`
    );
  });
});

///////////////////////// Helper functions/classes /////////////////////////

class ColorGenerator {
  constructor(identifiers) {
    let count = identifiers.length;
    let colors = randomColor({
      // Seed = 1000 generates acceptable colors.
      // See https://github.com/davidmerfield/randomColor/issues/136
      seed: 1000,
      count: count,
      luminosity: "light",
    });
    this.colorMap = new Map();
    for (let i = 0; i < count; i++) {
      this.colorMap.set(identifiers[i], colors[i]);
    }
  }

  getColor(identifier) {
    return this.colorMap.get(identifier);
  }
}

function buildLabelText(event) {
  return `${event.target}: ${event.type}`;
}

function getTooltipTextForEventNode(event) {
  // TODO: Truncate value.
  return event.value;
}
