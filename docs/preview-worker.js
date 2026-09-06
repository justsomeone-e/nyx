importScripts('evaluator.js');
self.onmessage = ({ data }) => {
  try {
    self.postMessage(NyxPreview.evaluateNyx(data));
  } catch (error) {
    self.postMessage({ output: [], error: error.message });
  }
};
