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
  cl("\n");
  if (node.type === "Return") {
    cl("Return value is:\n");
  } else {
    cl(
      `Value of %c${node.target} %cat line %c${node.level}%c:`,
      "color: #b43024",
      "",
      "color: #b43024",
      ""
    );
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
      // When there's only one property "repr", it means we currently can't rely
      // on JSON pickle for serialization. As a fallback, log the repr text.
      const keys = Object.keys(obj);
      if (keys.length === 1 && keys[0] === "repr") {
        cl(obj.repr);
        return;
      }
      cl(obj);
  }
}
