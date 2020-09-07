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
import { generateNodeUpdate, getInitialState, Loop } from "./loop.js";

let cl = console.log;

let traceGraph;

window.addEventListener("message", event => {
  if (!event.data.hasOwnProperty("events")) {
    return; // Server ready message.
  }

  console.log(event.data);
  traceGraph = new TraceGraph(event.data);
  traceGraph.initialize();
});

const options = {
  nodes: {
    shape: "box"
  },
  edges: {
    smooth: {
      type: "cubicBezier",
      forceDirection: "vertical"
    }
  },
  interaction: {
    dragNodes: false,
    hover: true
  },
  layout: {
    hierarchical: {
      direction: "UD", // From up to bottom.
      edgeMinimization: false // To not let edges overlap with nodes.
    }
  },
  physics: {
    hierarchicalRepulsion: {
      avoidOverlap: 1 // puts the most space around nodes to avoid overlapping.
    }
  },
  manipulation: {
    initiallyActive: true,
    addEdge: false,
    editEdge: false,
    addNode: false,
    deleteNode: false,
    deleteEdge: false,
    editNode: function(data, callback) {
      // filling in the popup DOM elements
      document.getElementById("node-operation").innerHTML = "Edit Loop Counter";
      editNode(data, cancelNodeEdit, callback);
    }
  }
};

// A method to draw round corner rectangle on canvas.
// From https://stackoverflow.com/a/7838871/2142577.
CanvasRenderingContext2D.prototype.roundRect = function(x, y, w, h, r) {
  if (w < 2 * r) {
    r = w / 2;
  }
  if (h < 2 * r) {
    r = h / 2;
  }
  this.beginPath();
  this.moveTo(x + r, y);
  this.arcTo(x + w, y, x + w, y + h, r);
  this.arcTo(x + w, y + h, x, y + h, r);
  this.arcTo(x, y + h, x, y, r);
  this.arcTo(x, y, x + w, y, r);
  this.closePath();
  return this;
};

class TraceGraph {
  constructor(data) {
    this.lines = new Set();
    this.events = data.events;
    this.loops = data.loops.map(
      loop => new Loop(loop.startOffset, loop.endOffset, loop.startLineno)
    );
    this.tracingResult = data.tracingResult;
    this.colorGenerator = new ColorGenerator(data.identifiers);
    this.nodes = new vis.DataSet([]);
    this.edges = new vis.DataSet([]);
    this.container = document.getElementById("vis");
    this.hoveredNodeId = undefined;
    this.network = new vis.Network(
      this.container,
      {
        nodes: this.nodes,
        edges: this.edges
      },
      options
    );
  }

  initialize() {
    let nodesToShow = [];
    let edgesToShow = [];
    let [initialEvents, _] = getInitialState(this.events, this.loops);

    // Add loop counter nodes.
    for (let i = 0; i < this.loops.length; i++) {
      let loop = this.loops[i];
      nodesToShow.push({
        title: "Loop counter",
        id: loop.id,
        level: loop.startLineno,
        label: "0",
        loop: loop,
        color: {
          background: "white"
        }
      });
      if (i < this.loops.length - 1) {
        edgesToShow.push(this.createHiddenEdge(loop.id, this.loops[i + 1].id));
      }
    }

    for (let event of initialEvents) {
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
              background: "rgba(0, 0, 0, 0)"
            }
          }
        });
      }
      nodesToShow.push(this.createNode(event));

      // Add edges.
      if (Object.prototype.hasOwnProperty.call(this.tracingResult, event.id)) {
        for (let source_event_id of this.tracingResult[event.id]) {
          edgesToShow.push({
            from: source_event_id,
            to: event.id,
            id: source_event_id + event.id
          });
        }
      }
    }

    // Add hidden edges so that lineno nodes are placed on the same vertical position.
    let lines = Array.from(this.lines);
    lines.sort();
    for (let i = 0; i < lines.length - 1; i++) {
      edgesToShow.push(this.createHiddenEdge(lines[i], lines[i + 1]));
    }

    cl(nodesToShow);

    this.nodes.add(nodesToShow);
    this.edges.add(edgesToShow);

    /*
     Manually draw tooltips to show each node's value on the trace path.
     */
    this.network.on("afterDrawing", ctx => {
      if (this.hoveredNodeId === undefined) {
        return;
      }

      let [tracePathNodeIds, tracePathEdgeIds] = findNodesAndEdgesOnTracePath(
        this.network,
        this.edges,
        this.hoveredNodeId
      );
      tracePathNodeIds = Array.from(tracePathNodeIds);
      tracePathEdgeIds = Array.from(tracePathEdgeIds);

      ctx.font = "14px consolas";
      ctx.strokeStyle = "#89897d";

      this.network.setSelection(
        {
          nodes: tracePathNodeIds,
          edges: tracePathEdgeIds
        },
        {
          highlightEdges: false
        }
      );

      for (let node of this.nodes.get(tracePathNodeIds)) {
        let text = getTooltipTextForEventNode(node);
        let pos = this.network.getPosition(node.id);
        let rectX = pos.x + 10;
        let rectY = pos.y - 33;
        let rectWidth = ctx.measureText(text).width + 20;
        let rectHeight = 25;

        ctx.fillStyle = "#f5f4ed";
        ctx.roundRect(rectX, rectY, rectWidth, rectHeight, 5).fill();
        ctx.roundRect(rectX, rectY, rectWidth, rectHeight, 5).stroke();
        ctx.fillStyle = "black";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        // Centers text at background rectangle's center.
        ctx.fillText(text, rectX + rectWidth / 2, rectY + rectHeight / 2);
      }
    });

    this.network.on("hoverNode", event => {
      let node = this.nodes.get(event.node);
      if (!node.hasOwnProperty("target")) {
        return;
      }
      this.hoveredNodeId = node.id;

      // console.clear();
      // TODO: show values of all local variables at this point.
      console.log(
        `${node.target}'s value at line ${node.level}: \n ${node.runtimeValue}`
      );
    });

    this.network.on("blurNode", event => {
      this.hoveredNodeId = undefined;
    });

    // Only show edit button when clicking on loop counter nodes, otherwise hide it.
    this.network.on("click", event => {
      let selectedNode = this.nodes.get(event.nodes[0]);
      setTimeout(() => {
        if (selectedNode.loop === undefined) {
          document.querySelector(".vis-manipulation").style.display = "none";
        } else {
          document.querySelector(
            ".vis-manipulation .vis-edit .vis-label"
          ).innerText = "Edit loop counter";
        }
      }, 0);
    });
  }

  createHiddenEdge(fromNode, toNode) {
    return {
      from: fromNode,
      to: toNode,
      color: {
        color: "rgba(0, 0, 0, 0)",
        hover: "rgba(0, 0, 0, 0)"
      }
    };
  }

  createNode(event) {
    return {
      id: event.id,
      level: event.lineno,
      label: buildLabelText(event),
      target: event.target,
      // "value" is reserved, use "runtimeValue" instead.
      runtimeValue: event.value,
      offset: event.offset,
      color: {
        background: this.colorGenerator.getColor(event.target),
        hover: {
          // Right now we let color keeps unchanged when hovering. We may slightly
          // change the color to make the node obvious.
          background: this.colorGenerator.getColor(event.target)
        }
      }
    };
  }
}

///////////////////////// Loop counter node related /////////////////////////

function editNode(node, cancelAction, callback) {
  document.getElementById("node-label").value = node.label;
  document.getElementById("node-saveButton").onclick = saveNodeData.bind(
    this,
    node,
    callback
  );
  document.getElementById("node-cancelButton").onclick = cancelAction.bind(
    this,
    callback
  );
  let popUp = document.getElementById("node-popUp");
  popUp.style.display = "block";

  // Insert instruction text to help users modify counters.
  let infoText = document.getElementById("counter_info");
  let infoTextNotExist = infoText === null;
  if (infoTextNotExist) {
    infoText = document.createElement("p");
    infoText.id = "counter_info";
  }
  infoText.innerText = `Counter max value: ${node.loop.maxCounter}`;
  infoText.hasWarning = false;
  if (infoTextNotExist) {
    popUp.insertBefore(infoText, null);
  }
}

function cancelNodeEdit(callback) {
  clearNodePopUp();
  callback(null);
}

function saveNodeData(node, callback) {
  let userSetCounterText = document.getElementById("node-label").value;
  let userSetCounterValue = parseInt(userSetCounterText);

  if (userSetCounterValue > node.loop.maxCounter) {
    let infoText = document.getElementById("counter_info");
    if (!infoText.hasWarning) {
      infoText.innerHTML =
        infoText.innerHTML +
        "<p style='color:red'>Counter exceeds upper limit</p>";
      infoText.hasWarning = true;
    }
    return;
  }

  node.label = userSetCounterText;
  node.loop.counter = userSetCounterValue;
  traceGraph.nodes.update({ id: node.loop.id, label: userSetCounterText });

  let visibleEvents = traceGraph.nodes.get({
    filter: node => {
      return node.hasOwnProperty("offset");
    }
  });

  // cl(visibleEvents);
  let [eventsToHide, eventsToShow] = generateNodeUpdate(
    traceGraph.events,
    visibleEvents,
    node.loop
  );

  for (let event of eventsToHide.values()) {
    traceGraph.nodes.remove(event);
  }
  for (let event of eventsToShow.values()) {
    cl(traceGraph.createNode(event));
    traceGraph.nodes.update(traceGraph.createNode(event));
  }

  clearNodePopUp();
  callback(node);
}

function clearNodePopUp() {
  document.getElementById("node-saveButton").onclick = null;
  document.getElementById("node-cancelButton").onclick = null;
  document.getElementById("node-popUp").style.display = "none";
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
      luminosity: "light"
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

function getTooltipTextForEventNode(node) {
  // TODO: Truncate value.
  return node.runtimeValue;
}

/*
Given a node, find all node on the trace path. Here we not only find all sources nodes,
we also find all nodes that is a consequence of the given node, both directly and indirectly.
    A
   / \
  B  D
 /
C

Given the above graph and node "B", this function should return "A", "B", "C".

Trace graph does not have loop, so we don't need to check repeated nodes during recursion.
 */
function findNodesAndEdgesOnTracePath(
  network,
  edges,
  nodeId,
  directions = ["from", "to"]
) {
  let resultNodes = new Set([nodeId]);
  let resultEdges = new Set();

  for (let direction of directions) {
    for (let connectedNode of network.getConnectedNodes(nodeId, direction)) {
      if (direction === "from") {
        resultEdges.add(edges.get(connectedNode + nodeId).id);
      } else if (direction === "to") {
        resultEdges.add(edges.get(nodeId + connectedNode).id);
      }
      let [
        indirectConnectedNodes,
        indirectConnectedEdges
      ] = findNodesAndEdgesOnTracePath(network, edges, connectedNode, [
        direction
      ]);
      for (let indirectConnectedNode of indirectConnectedNodes) {
        resultNodes.add(indirectConnectedNode);
      }
      for (let indirectConnectedEdge of indirectConnectedEdges) {
        resultEdges.add(indirectConnectedEdge);
      }
    }
  }

  return [resultNodes, resultEdges];
}
