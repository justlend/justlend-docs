# API Playground

Interactive sandbox for the JustLend DAO API. Pick an endpoint on the left, fill in parameters, click **Try It** to fire a real request and see the live response.

For the human‑readable reference (tables, USDD/mining semantics, field units), see [APIs](./apis.md).

<style>
  /* Give Scalar enough room inside the MkDocs Material content area */
  #api-reference { display: block; min-height: 90vh; }
</style>

<div id="api-reference"></div>

<script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
<script>
  Scalar.createApiReference('#api-reference', {
    url: 'apis/justlend_apis.yaml',

    // Default + only available code sample: curl
    defaultHttpClient: { targetKey: 'shell', clientKey: 'curl' },
    hiddenClients: {
      shell: ['httpie', 'wget'],
      javascript: true,
      node: true,
      python: true,
      ruby: true,
      php: true,
      java: true,
      csharp: true,
      go: true,
      c: true,
      swift: true,
      kotlin: true,
      objc: true,
      ocaml: true,
      powershell: true,
      r: true,
    },
  });
</script>
