# Examples

## Register and version a prompt

```python
from tokenhelm_prompt import YamlRegistry

reg = YamlRegistry("prompts.yaml")
reg.register("invoice_summary", owner="ana", application="billing",
             environment="prod", template="Summarize {invoice_id} for {customer}")

# Evolve it — a new immutable version is created; v1 is retained.
reg.add_version("invoice_summary", template="TL;DR invoice {invoice_id}", created_by="ana")
print([(v.version, v.status.value) for v in reg.versions("invoice_summary")])
# [('v1', 'deprecated'), ('v2', 'active')]
```

## Attribute calls automatically

```python
from tokenhelm import TokenHelm, DefaultEventDispatcher
from tokenhelm_prompt import tracker, make_dispatcher

tracker.use_registry(reg)
th = TokenHelm(dispatcher=make_dispatcher(DefaultEventDispatcher()))

with tracker.prompt("invoice_summary"):
    th.track(response)        # attributed to invoice_summary@v2
```

## Decorator + async

```python
from tokenhelm_prompt import prompt

@prompt("invoice_summary")
async def summarize(client, invoice):
    return await client.responses.create(...)
```

## Nested scopes

```python
with tracker.prompt("invoice"):
    # ... attributed to "invoice"
    with tracker.prompt("translate"):
        ...                   # attributed to "translate"
    # ... attributed to "invoice" again
```

## Analytics & export

```python
from tokenhelm_prompt import analytics

for a in analytics.by_version():
    print(a.prompt_name, a.prompt_version, a.calls, a.failures, a.cost)

analytics.export("csv", "by_version.csv")
analytics.export("json", "by_version.json")
```

## Optional: LangChain

```python
from tokenhelm_prompt.integrations.langchain import make_callback

handler = make_callback("invoice_summary")   # imports langchain_core lazily
chain.invoke(inputs, config={"callbacks": [handler]})
```
