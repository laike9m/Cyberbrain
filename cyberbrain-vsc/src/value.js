/*
https://github.com/laike9m/Cyberbrain/issues/8

Improve object inspection, improve clarity when displaying values in the console
and make them more "Python-like", while loosing as few information as possible.
 */

let cl = console.log;

// An enum of Js object types.
const Types = Object.freeze({ NULL: "Null", STRING: "String" });

// From https://bonsaiden.github.io/JavaScript-Garden/#types.typeof
// Returns the type of a Js object. Possible return values:
// Arguments, Array, Boolean, Date, Error, Function, JSON, Math, Number, Object, RegExp, String, NULL.
function getType(obj) {
  return Object.prototype.toString.call(obj).slice(8, -1);
}

// Displays a Js object in devtools console so that it looks like a Python object.
//
// See http://shorturl.at/gkzJS for how format of output.
export function displayValueInConsole(node) {
  if (node.type === "Return") {
    cl("Return value is:\n");
  } else {
    cl(`${node.target}'s value at line ${node.level}:\n`);
  }
  const obj = node.runtimeValue;

  switch (getType(obj)) {
    case Types.NULL:
      cl("None");
      break;
    case Types.STRING:
      cl('"' + `%c${obj}` + '%c"', "color: #b43024", "");
      break;
    default:
      cl(obj);
  }
}

// TODO: Truncate value or make it display in multilines.
// Gets the text representation of a Js object that looks like a Python object.
export function getTooltipText(obj) {
  switch (getType(obj)) {
    case Types.NULL:
      return "None";
    case Types.STRING:
      return `"${obj}"`;
    default:
      // To keep the brackets of arrays.
      return JSON.stringify(obj);
  }
}
