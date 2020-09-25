/*
https://github.com/laike9m/Cyberbrain/issues/8

Improve object inspection, improve clarity when displaying values in the console
and make them more "Python-like", while loosing as few information as possible.
 */

let cl = console.log;

// TODO: Generalize special value handling.
export function displayValueInConsole(node) {
  if (node.type === "Return") {
    cl("Return value is:\n");
  } else {
    cl(`${node.target}'s value at line ${node.level}:\n`);
  }

  let jsValue = node.runtimeValue;
  cl(convertValueFromJsToPython(jsValue));
}

// TODO: Truncate value or make values multiline.
export function getTooltipTextForEventNode(node) {
  return convertValueFromJsToPython(node.runtimeValue);
}

function convertValueFromJsToPython(jsValue) {
  if (jsValue === null) {
    return "None";
  } else {
    return jsValue;
  }
}
