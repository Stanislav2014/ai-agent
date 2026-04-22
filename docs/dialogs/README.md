# Dialogs — acceptance-артефакты

Логи живых прогонов агента против lemonade-server (`Qwen3-4B-Instruct-2507-GGUF`).

| Файл | Задача | Ожидание | Результат |
|---|---|---|---|
| `test1-calculator.log` | `Посчитай (123 + 456) * 2` | final_answer содержит `1158` | ✅ `1158` за 2 шага |
| `test2-read-file.log` | `Прочитай файл /workspace/test.txt и скажи сколько в нём строк` | final_answer содержит `5` | ✅ `5` за 2 шага |
| `test3-http-get.log` | `Сделай GET запрос к https://api.github.com и верни HTTP статус-код` | final_answer содержит `200` | ✅ `200 OK` за 2 шага |

В каждом файле — полный stdout: заголовок `Task:` / `Model:`, блоки `[Step N]` с `Thought:/Action:/Args:/Observation:`, финальный `=== ANSWER ===`.

Прогон:
```
make run TASK='Посчитай (123 + 456) * 2'
make run TASK='Прочитай файл /workspace/test.txt и скажи сколько в нём строк'
make run TASK='Сделай GET запрос к https://api.github.com и верни HTTP статус-код'
```

Воспроизводимо через pytest:
```
make test-int
```
