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

I would love to write webview code in TS as well, but so far TS support in vis-network
is poor, see: https://github.com/visjs/vis-network/issues/930

*/

// The .js suffix is needed to make import work in vsc webview.
import { getInitialState, Loop } from "./loop.js";

window.addEventListener("message", (event) => {
  if (!event.data.hasOwnProperty("events")) {
    return; // Server ready message.
  }

  console.log(event.data);
  const graph = new TraceGraph(event.data);
  graph.initialize();
});

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

class TraceGraph {
  constructor(data) {
    this.lines = new Set();
    this.events = data.events;
    this.loops = data.loops.map(
      (loop) => new Loop(loop.startOffset, loop.endOffset, loop.startLineno)
    );
    this.tracingResult = data.tracingResult;
    this.colorGenerator = new ColorGenerator(data.identifiers);
    this.nodes = new vis.DataSet([]);
    this.edges = new vis.DataSet([]);
    this.container = document.getElementById("vis");
    this.network = new vis.Network(
      this.container,
      {
        nodes: this.nodes,
        edges: this.edges,
      },
      options
    );
  }

  initialize() {
    let nodesToShow = [];
    let edgesToShow = [];
    let [initialEvents, _] = getInitialState(this.events, this.loops);

    for (let event of initialEvents) {
      if (event.type === "JumpBackToLoopStart") continue;

      let linenoString = event.lineno.toString();
      if (!this.lines.has(linenoString)) {
        // Adds a "virtual node" to show line number. This node should precede other nodes
        // on the same level. According to https://github.com/visjs/vis-network/issues/926,
        // the order is not deterministic, but seems it's roughly the same as the insertion
        // order.
        this.lines.add(linenoString);
        nodesToShow.push({
          title: `Line ${event.lineno}`,
          id: linenoString,
          level: event.lineno,
          label: linenoString,
          borderWidth: 0,
          // Disable physics so the lineno nodes are not pushed away to the left.
          physics: false,
          color: {
            border: "rgba(0, 0, 0, 0)",
            background: "rgba(0, 0, 0, 0)",
            hover: {
              background: "rgba(0, 0, 0, 0)",
            },
          },
        });
      }
      nodesToShow.push(this.createNode(event));

      // Add edges.
      if (Object.prototype.hasOwnProperty.call(this.tracingResult, event.uid)) {
        for (let source_event_uid of this.tracingResult[event.uid]) {
          edgesToShow.push({
            from: source_event_uid,
            to: event.uid,
          });
        }
      }
    }

    // Add hidden edges so that lineno nodes are placed on the same vertical position.
    let lines = Array.from(this.lines);
    lines.sort();
    for (let i = 0; i < lines.length - 1; i++) {
      edgesToShow.push({
        from: lines[i],
        to: lines[i + 1],
        color: {
          color: "rgba(0, 0, 0, 0)",
          hover: "rgba(0, 0, 0, 0)",
        },
      });
    }

    this.nodes.add(nodesToShow);
    this.edges.add(edgesToShow);

    this.network.on("hoverNode", (event) => {
      let node = this.nodes.get(event.node);
      if (!node.hasOwnProperty("target")) {
        return;
      }
      console.log(
        `${node.target}'s value at line ${node.level}: \n ${node.runtimeValue}`
      );
    });
  }

  createNode(event) {
    return {
      title: getTooltipTextForEventNode(event),
      id: event.uid,
      level: event.lineno,
      label: buildLabelText(event),
      target: event.target,
      // "value" is reserved, use "runtimeValue" instead.
      runtimeValue: event.value,
      color: {
        background: this.colorGenerator.getColor(event.target),
        hover: {
          // Right now we let color keeps unchanged when hovering. We may slightly
          // change the color to make the node obvious.
          background: this.colorGenerator.getColor(event.target),
        },
      },
    };
  }
}

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
