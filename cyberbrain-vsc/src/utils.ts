
// TODO: Learn from
//   https://github.com/cuthbertLab/jsonpickleJS/blob/master/js/unpickler.js
//   and implement a better version of decode.
//   Maybe use https://stackoverflow.com/a/46132163.
export function decodeJson(jsonString: string) {
    return JSON.parse(jsonString);
}