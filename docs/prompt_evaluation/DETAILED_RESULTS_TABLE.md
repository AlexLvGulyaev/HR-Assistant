# HRA-EXP-V1: Детализированные результаты по всем 90 замерам

**Эксперимент:** HRA-EXP-V1
**Дата:** 2026-06-25
**Источник:** Production PostgreSQL database

---

## Структура таблицы

Каждая строка представляет пару **резюме + вакансия** с результатами трёх вариантов:

| Колонка | Описание |
|---------|----------|
| **Case** | Код кейса |
| **Кандидат** | Имя и желаемая позиция |
| **Вакансия** | Название вакансии |
| **Judge** | Score (J) + Decision — эталонная оценка от gpt-4.1 |
| **Prompt A** | Score (A) + Decision + Delta от Judge + Latency |
| **Prompt B** | Score (B) + Decision + Delta от Judge + Latency |

**Delta** = Model Score - Judge Score (положительная = переоценка, отрицательная = недооценка)

---

## 1. Borderline кейсы (10 кандидатов × 3 вакансии = 30 пар)

Пограничные случаи, где решение неочевидно.

| Case | Кандидат | Вакансия | Judge (J) | Prompt A | Prompt B |
|------|----------|----------|-----------|----------|----------|
| HRA-EVAL-000021 | Григорьев Дмитрий Александрович<br>(Business Analyst) | Prompt Engineer / AI Automation Specialist | **52** no_match | **40** no_match<br>Δ=-12, 1963ms | **37** no_match<br>Δ=-15, 1964ms |
| HRA-EVAL-000021 | Григорьев Дмитрий Александрович<br>(Business Analyst) | Системный аналитик | **70** match | **70** match<br>Δ=0, 1784ms | **71** match<br>Δ=+1, 2066ms |
| HRA-EVAL-000021 | Григорьев Дмитрий Александрович<br>(Business Analyst) | Специалист по разметке данных | **31** no_match | **15** no_match<br>Δ=-16, 2203ms | **0** no_match<br>Δ=-31, 1894ms |
| HRA-EVAL-000022 | Николаева Анна Петровна<br>(Prompt Engineer) | Prompt Engineer / AI Automation Specialist | **63** match | **65** match<br>Δ=+2, 1829ms | **78** match<br>Δ=+15, 1781ms |
| HRA-EVAL-000022 | Николаева Анна Петровна<br>(Prompt Engineer) | Системный аналитик | **30** no_match | **30** no_match<br>Δ=0, 1614ms | **10** no_match<br>Δ=-20, 2227ms |
| HRA-EVAL-000022 | Николаева Анна Петровна<br>(Prompt Engineer) | Специалист по разметке данных | **29** no_match | **35** no_match<br>Δ=+6, 1707ms | **10** no_match<br>Δ=-19, 1660ms |
| HRA-EVAL-000023 | Степанова Виктория Олеговна<br>(Data Analyst) | Prompt Engineer / AI Automation Specialist | **45** no_match | **25** no_match<br>Δ=-20, 2097ms | **29** no_match<br>Δ=-16, 2625ms |
| HRA-EVAL-000023 | Степанова Виктория Олеговна<br>(Data Analyst) | Системный аналитик | **61** match | **60** match<br>Δ=-1, 1915ms | **40** no_match<br>Δ=-21, 1942ms |
| HRA-EVAL-000023 | Степанова Виктория Олеговна<br>(Data Analyst) | Специалист по разметке данных | **37** no_match | **35** no_match<br>Δ=-2, 1950ms | **11** no_match<br>Δ=-26, 2743ms |
| HRA-EVAL-000024 | Михайлов Илья Сергеевич<br>(Product Manager) | Prompt Engineer / AI Automation Specialist | **64** no_match | **65** match<br>Δ=+1, 2194ms | **52** no_match<br>Δ=-12, 1930ms |
| HRA-EVAL-000024 | Михайлов Илья Сергеевич<br>(Product Manager) | Системный аналитик | **59** no_match | **45** no_match<br>Δ=-14, 1906ms | **25** no_match<br>Δ=-34, 1864ms |
| HRA-EVAL-000024 | Михайлов Илья Сергеевич<br>(Product Manager) | Специалист по разметке данных | **30** no_match | **10** no_match<br>Δ=-20, 2239ms | **0** no_match<br>Δ=-30, 2379ms |
| HRA-EVAL-000025 | Кузнецова Елена Александровна<br>(Junior Data Analyst) | Prompt Engineer / AI Automation Specialist | **30** no_match | **25** no_match<br>Δ=-5, 1849ms | **10** no_match<br>Δ=-20, 2034ms |
| HRA-EVAL-000025 | Кузнецова Елена Александровна<br>(Junior Data Analyst) | Системный аналитик | **22** no_match | **30** no_match<br>Δ=+8, 1889ms | **35** no_match<br>Δ=+13, 2314ms |
| HRA-EVAL-000025 | Кузнецова Елена Александровна<br>(Junior Data Analyst) | Специалист по разметке данных | **62** match | **70** match<br>Δ=+8, 1973ms | **75** match<br>Δ=+13, 3233ms |
| HRA-EVAL-000026 | Соколов Артём Викторович<br>(QA Engineer) | Prompt Engineer / AI Automation Specialist | **51** no_match | **50** no_match<br>Δ=-1, 1920ms | **55** no_match<br>Δ=+4, 1843ms |
| HRA-EVAL-000026 | Соколов Артём Викторович<br>(QA Engineer) | Системный аналитик | **62** no_match | **50** no_match<br>Δ=-12, 1906ms | **47** no_match<br>Δ=-15, 1931ms |
| HRA-EVAL-000026 | Соколов Артём Викторович<br>(QA Engineer) | Специалист по разметке данных | **31** no_match | **10** no_match<br>Δ=-21, 2038ms | **17** no_match<br>Δ=-14, 2177ms |
| HRA-EVAL-000027 | Петрова Светлана Николаевна<br>(Technical Writer) | Prompt Engineer / AI Automation Specialist | **58** no_match | **45** no_match<br>Δ=-13, 1717ms | **52** no_match<br>Δ=-6, 2475ms |
| HRA-EVAL-000027 | Петрова Светлана Николаевна<br>(Technical Writer) | Системный аналитик | **58** no_match | **35** no_match<br>Δ=-23, 2093ms | **37** no_match<br>Δ=-21, 2824ms |
| HRA-EVAL-000027 | Петрова Светлана Николаевна<br>(Technical Writer) | Специалист по разметке данных | **47** no_match | **50** no_match<br>Δ=+3, 1814ms | **25** no_match<br>Δ=-22, 1942ms |
| HRA-EVAL-000028 | Смирнов Андрей Дмитриевич<br>(Junior Системный аналитик) | Prompt Engineer / AI Automation Specialist | **14** no_match | **15** no_match<br>Δ=+1, 1898ms | **30** no_match<br>Δ=+16, 3486ms |
| HRA-EVAL-000028 | Смирнов Андрей Дмитриевич<br>(Junior Системный аналитик) | Системный аналитик | **43** no_match | **50** no_match<br>Δ=+7, 1836ms | **88** match<br>Δ=+45, 2697ms |
| HRA-EVAL-000028 | Смирнов Андрей Дмитриевич<br>(Junior Системный аналитик) | Специалист по разметке данных | **38** no_match | **20** no_match<br>Δ=-18, 1855ms | **30** no_match<br>Δ=-8, 2778ms |
| HRA-EVAL-000029 | Волков Павел Андреевич<br>(ML Engineer) | Prompt Engineer / AI Automation Specialist | **54** no_match | **50** no_match<br>Δ=-4, 2744ms | **35** no_match<br>Δ=-19, 2165ms |
| HRA-EVAL-000029 | Волков Павел Андреевич<br>(ML Engineer) | Системный аналитик | **39** no_match | **20** no_match<br>Δ=-19, 2426ms | **25** no_match<br>Δ=-14, 2187ms |
| HRA-EVAL-000029 | Волков Павел Андреевич<br>(ML Engineer) | Специалист по разметке данных | **31** no_match | **20** no_match<br>Δ=-11, 2352ms | **0** no_match<br>Δ=-31, 2113ms |
| HRA-EVAL-000030 | Козлова Мария Александровна<br>(Content Manager) | Prompt Engineer / AI Automation Specialist | **20** no_match | **20** no_match<br>Δ=0, 1985ms | **17** no_match<br>Δ=-3, 2016ms |
| HRA-EVAL-000030 | Козлова Мария Александровна<br>(Content Manager) | Системный аналитик | **31** no_match | **10** no_match<br>Δ=-21, 1761ms | **18** no_match<br>Δ=-13, 2607ms |
| HRA-EVAL-000030 | Козлова Мария Александровна<br>(Content Manager) | Специалист по разметке данных | **64** match | **50** no_match<br>Δ=-14, 1982ms | **48** no_match<br>Δ=-16, 6559ms |

---

## 2. Obvious Match кейсы (10 кандидатов × 3 вакансии = 30 пар)

Очевидные совпадения, где кандидат должен получить high score.

| Case | Кандидат | Вакансия | Judge (J) | Prompt A | Prompt B |
|------|----------|----------|-----------|----------|----------|
| HRA-EVAL-000001 | Иванов Иван Иванович<br>(Системный аналитик) | Prompt Engineer / AI Automation Specialist | **58** no_match | **55** no_match<br>Δ=-3, 1717ms | **37** no_match<br>Δ=-21, 2216ms |
| HRA-EVAL-000001 | Иванов Иван Иванович<br>(Системный аналитик) | Системный аналитик | **98** match | **100** match<br>Δ=+2, 2020ms | **97** match<br>Δ=-1, 1712ms |
| HRA-EVAL-000001 | Иванов Иван Иванович<br>(Системный аналитик) | Специалист по разметке данных | **39** no_match | **10** no_match<br>Δ=-29, 2451ms | **15** no_match<br>Δ=-24, 1623ms |
| HRA-EVAL-000002 | Петрова Мария Сергеевна<br>(Prompt Engineer) | Prompt Engineer / AI Automation Specialist | **97** match | **95** match<br>Δ=-2, 1970ms | **92** match<br>Δ=-5, 1925ms |
| HRA-EVAL-000002 | Петрова Мария Сергеевна<br>(Prompt Engineer) | Системный аналитик | **58** no_match | **35** no_match<br>Δ=-23, 1992ms | **37** no_match<br>Δ=-21, 2101ms |
| HRA-EVAL-000002 | Петрова Мария Сергеевна<br>(Prompt Engineer) | Специалист по разметке данных | **47** no_match | **50** no_match<br>Δ=+3, 2002ms | **18** no_match<br>Δ=-29, 2270ms |
| HRA-EVAL-000003 | Сидоров Алексей Петрович<br>(Специалист по разметке данных) | Prompt Engineer / AI Automation Specialist | **35** no_match | **20** no_match<br>Δ=-15, 2074ms | **10** no_match<br>Δ=-25, 2012ms |
| HRA-EVAL-000003 | Сидоров Алексей Петрович<br>(Специалист по разметке данных) | Системный аналитик | **11** no_match | **10** no_match<br>Δ=-1, 1868ms | **10** no_match<br>Δ=-1, 1867ms |
| HRA-EVAL-000003 | Сидоров Алексей Петрович<br>(Специалист по разметке данных) | Специалист по разметке данных | **82** match | **85** match<br>Δ=+3, 1960ms | **95** match<br>Δ=+13, 1764ms |
| HRA-EVAL-000004 | Козлова Анна Дмитриевна<br>(Системный аналитик) | Prompt Engineer / AI Automation Specialist | **56** no_match | **35** no_match<br>Δ=-21, 1856ms | **55** no_match<br>Δ=-1, 3028ms |
| HRA-EVAL-000004 | Козлова Анна Дмитриевна<br>(Системный аналитик) | Системный аналитик | **90** match | **90** match<br>Δ=0, 2012ms | **87** match<br>Δ=-3, 2328ms |
| HRA-EVAL-000004 | Козлова Анна Дмитриевна<br>(Системный аналитик) | Специалист по разметке данных | **30** no_match | **10** no_match<br>Δ=-20, 1960ms | **10** no_match<br>Δ=-20, 2740ms |
| HRA-EVAL-000005 | Новиков Дмитрий Олегович<br>(Junior Системный аналитик) | Prompt Engineer / AI Automation Specialist | **36** no_match | **25** no_match<br>Δ=-11, 1943ms | **25** no_match<br>Δ=-11, 2278ms |
| HRA-EVAL-000005 | Новиков Дмитрий Олегович<br>(Junior Системный аналитик) | Системный аналитик | **65** match | **65** match<br>Δ=0, 1991ms | **73** match<br>Δ=+8, 2211ms |
| HRA-EVAL-000005 | Новиков Дмитрий Олегович<br>(Junior Системный аналитик) | Специалист по разметке данных | **39** no_match | **15** no_match<br>Δ=-24, 1584ms | **0** no_match<br>Δ=-39, 1782ms |
| HRA-EVAL-000006 | Морозова Елена Викторовна<br>(Senior Prompt Engineer) | Prompt Engineer / AI Automation Specialist | **97** match | **100** match<br>Δ=+3, 1907ms | **90** match<br>Δ=-7, 1640ms |
| HRA-EVAL-000006 | Морозова Елена Викторовна<br>(Senior Prompt Engineer) | Системный аналитик | **52** no_match | **40** no_match<br>Δ=-12, 1927ms | **30** no_match<br>Δ=-22, 2542ms |
| HRA-EVAL-000006 | Морозова Елена Викторовна<br>(Senior Prompt Engineer) | Специалист по разметке данных | **41** no_match | **35** no_match<br>Δ=-6, 2250ms | **0** no_match<br>Δ=-41, 1976ms |
| HRA-EVAL-000007 | Волков Сергей Игоревич<br>(Аналитик) | Prompt Engineer / AI Automation Specialist | **60** match | **50** no_match<br>Δ=-10, 2019ms | **52** no_match<br>Δ=-8, 2233ms |
| HRA-EVAL-000007 | Волков Сергей Игоревич<br>(Аналитик) | Системный аналитик | **96** match | **90** match<br>Δ=-6, 2888ms | **95** match<br>Δ=-1, 2088ms |
| HRA-EVAL-000007 | Волков Сергей Игоревич<br>(Аналитик) | Специалист по разметке данных | **43** no_match | **30** no_match<br>Δ=-13, 2146ms | **20** no_match<br>Δ=-23, 2048ms |
| HRA-EVAL-000008 | Кузнецов Павел Андреевич<br>(AI Engineer) | Prompt Engineer / AI Automation Specialist | **89** match | **85** match<br>Δ=-4, 2299ms | **87** match<br>Δ=-2, 2004ms |
| HRA-EVAL-000008 | Кузнецов Павел Андреевич<br>(AI Engineer) | Системный аналитик | **56** no_match | **55** no_match<br>Δ=-1, 2273ms | **35** no_match<br>Δ=-21, 2013ms |
| HRA-EVAL-000008 | Кузнецов Павел Андреевич<br>(AI Engineer) | Специалист по разметке данных | **42** no_match | **25** no_match<br>Δ=-17, 2545ms | **18** no_match<br>Δ=-24, 2036ms |
| HRA-EVAL-000009 | Лебедева Ольга Сергеевна<br>(Data Specialist) | Prompt Engineer / AI Automation Specialist | **26** no_match | **40** no_match<br>Δ=+14, 1562ms | **18** no_match<br>Δ=-8, 2026ms |
| HRA-EVAL-000009 | Лебедева Ольга Сергеевна<br>(Data Specialist) | Системный аналитик | **41** no_match | **40** no_match<br>Δ=-1, 1877ms | **28** no_match<br>Δ=-13, 2134ms |
| HRA-EVAL-000009 | Лебедева Ольга Сергеевна<br>(Data Specialist) | Специалист по разметке данных | **81** match | **80** match<br>Δ=-1, 1733ms | **78** match<br>Δ=-3, 2291ms |
| HRA-EVAL-000010 | Попов Максим Викторович<br>(Системный аналитик) | Prompt Engineer / AI Automation Specialist | **62** match | **50** no_match<br>Δ=-12, 1700ms | **52** no_match<br>Δ=-10, 2008ms |
| HRA-EVAL-000010 | Попов Максим Викторович<br>(Системный аналитик) | Системный аналитик | **98** match | **100** match<br>Δ=+2, 2165ms | **97** match<br>Δ=-1, 2981ms |
| HRA-EVAL-000010 | Попов Максим Викторович<br>(Системный аналитик) | Специалист по разметке данных | **36** no_match | **10** no_match<br>Δ=-26, 2192ms | **25** no_match<br>Δ=-11, 1914ms |

---

## 3. Obvious No-Match кейсы (10 кандидатов × 3 вакансии = 30 пар)

Очевидные несовпадения, где кандидат должен получить low score.

| Case | Кандидат | Вакансия | Judge (J) | Prompt A | Prompt B |
|------|----------|----------|-----------|----------|----------|
| HRA-EVAL-000011 | Смирнов Артём Павлович<br>(Java Developer) | Prompt Engineer / AI Automation Specialist | **33** no_match | **10** no_match<br>Δ=-23, 2017ms | **0** no_match<br>Δ=-33, 2178ms |
| HRA-EVAL-000011 | Смирнов Артём Павлович<br>(Java Developer) | Системный аналитик | **20** no_match | **0** no_match<br>Δ=-20, 2169ms | **15** no_match<br>Δ=-5, 2258ms |
| HRA-EVAL-000011 | Смирнов Артём Павлович<br>(Java Developer) | Специалист по разметке данных | **12** no_match | **0** no_match<br>Δ=-12, 2125ms | **0** no_match<br>Δ=-12, 2264ms |
| HRA-EVAL-000012 | Крылова Дарья Александровна<br>(UI/UX Designer) | Prompt Engineer / AI Automation Specialist | **31** no_match | **40** no_match<br>Δ=+9, 2000ms | **19** no_match<br>Δ=-12, 2152ms |
| HRA-EVAL-000012 | Крылова Дарья Александровна<br>(UI/UX Designer) | Системный аналитик | **49** no_match | **40** no_match<br>Δ=-9, 1865ms | **20** no_match<br>Δ=-29, 2207ms |
| HRA-EVAL-000012 | Крылова Дарья Александровна<br>(UI/UX Designer) | Специалист по разметке данных | **21** no_match | **10** no_match<br>Δ=-11, 2204ms | **0** no_match<br>Δ=-21, 2061ms |
| HRA-EVAL-000013 | Зайцев Никита Александрович<br>(Стажёр) | Prompt Engineer / AI Automation Specialist | **20** no_match | **5** no_match<br>Δ=-15, 1623ms | **30** no_match<br>Δ=+10, 3753ms |
| HRA-EVAL-000013 | Зайцев Никита Александрович<br>(Стажёр) | Системный аналитик | **22** no_match | **35** no_match<br>Δ=+13, 1931ms | **30** no_match<br>Δ=+8, 3034ms |
| HRA-EVAL-000013 | Зайцев Никита Александрович<br>(Стажёр) | Специалист по разметке данных | **21** no_match | **35** no_match<br>Δ=+14, 2165ms | **30** no_match<br>Δ=+9, 1976ms |
| HRA-EVAL-000014 | Соколова Анна Михайловна<br>(Marketing Manager) | Prompt Engineer / AI Automation Specialist | **38** no_match | **40** no_match<br>Δ=+2, 1989ms | **25** no_match<br>Δ=-13, 2247ms |
| HRA-EVAL-000014 | Соколова Анна Михайловна<br>(Marketing Manager) | Системный аналитик | **47** no_match | **35** no_match<br>Δ=-12, 2003ms | **25** no_match<br>Δ=-22, 2513ms |
| HRA-EVAL-000014 | Соколова Анна Михайловна<br>(Marketing Manager) | Специалист по разметке данных | **26** no_match | **10** no_match<br>Δ=-16, 1907ms | **0** no_match<br>Δ=-26, 2308ms |
| HRA-EVAL-000015 | Козлов Игорь Сергеевич<br>(Продавец-консультант) | Prompt Engineer / AI Automation Specialist | **20** no_match | **0** no_match<br>Δ=-20, 3006ms | **10** no_match<br>Δ=-10, 1968ms |
| HRA-EVAL-000015 | Козлов Игорь Сергеевич<br>(Продавец-консультант) | Системный аналитик | **5** no_match | **0** no_match<br>Δ=-5, 1923ms | **18** no_match<br>Δ=+13, 2808ms |
| HRA-EVAL-000015 | Козлов Игорь Сергеевич<br>(Продавец-консультант) | Специалист по разметке данных | **31** no_match | **25** no_match<br>Δ=-6, 2527ms | **18** no_match<br>Δ=-13, 1904ms |
| HRA-EVAL-000016 | Петров Василий Иванович<br>(Водитель) | Prompt Engineer / AI Automation Specialist | **17** no_match | **20** no_match<br>Δ=+3, 2084ms | **30** no_match<br>Δ=+13, 1654ms |
| HRA-EVAL-000016 | Петров Василий Иванович<br>(Водитель) | Системный аналитик | **18** no_match | **20** no_match<br>Δ=+2, 2007ms | **30** no_match<br>Δ=+12, 1898ms |
| HRA-EVAL-000016 | Петров Василий Иванович<br>(Водитель) | Специалист по разметке данных | **24** no_match | **15** no_match<br>Δ=-9, 1734ms | **35** no_match<br>Δ=+11, 1952ms |
| HRA-EVAL-000017 | Белова Екатерина Павловна<br>(HR Manager) | Prompt Engineer / AI Automation Specialist | **22** no_match | **40** no_match<br>Δ=+18, 2241ms | **17** no_match<br>Δ=-5, 1576ms |
| HRA-EVAL-000017 | Белова Екатерина Павловна<br>(HR Manager) | Системный аналитик | **36** no_match | **25** no_match<br>Δ=-11, 2464ms | **18** no_match<br>Δ=-18, 1987ms |
| HRA-EVAL-000017 | Белова Екатерина Павловна<br>(HR Manager) | Специалист по разметке данных | **29** no_match | **10** no_match<br>Δ=-19, 2670ms | **0** no_match<br>Δ=-29, 1879ms |
| HRA-EVAL-000018 | Фёдорова Наталья Викторовна<br>(Бухгалтер) | Prompt Engineer / AI Automation Specialist | **19** no_match | **10** no_match<br>Δ=-9, 2308ms | **12** no_match<br>Δ=-7, 2107ms |
| HRA-EVAL-000018 | Фёдорова Наталья Викторовна<br>(Бухгалтер) | Системный аналитик | **20** no_match | **15** no_match<br>Δ=-5, 2080ms | **25** no_match<br>Δ=+5, 2156ms |
| HRA-EVAL-000018 | Фёдорова Наталья Викторовна<br>(Бухгалтер) | Специалист по разметке данных | **34** no_match | **10** no_match<br>Δ=-24, 1987ms | **0** no_match<br>Δ=-34, 2692ms |
| HRA-EVAL-000019 | Романова Мария Андреевна<br>(Переводчик) | Prompt Engineer / AI Automation Specialist | **30** no_match | **35** no_match<br>Δ=+5, 3065ms | **25** no_match<br>Δ=-5, 2092ms |
| HRA-EVAL-000019 | Романова Мария Андреевна<br>(Переводчик) | Системный аналитик | **13** no_match | **15** no_match<br>Δ=+2, 2174ms | **25** no_match<br>Δ=+12, 1856ms |
| HRA-EVAL-000019 | Романова Мария Андреевна<br>(Переводчик) | Специалист по разметке данных | **58** no_match | **40** no_match<br>Δ=-18, 1982ms | **25** no_match<br>Δ=-33, 2074ms |
| HRA-EVAL-000020 | Орлов Андрей Владимирович<br>(Врач) | Prompt Engineer / AI Automation Specialist | **19** no_match | **20** no_match<br>Δ=+1, 2123ms | **32** no_match<br>Δ=+13, 2064ms |
| HRA-EVAL-000020 | Орлов Андрей Владимирович<br>(Врач) | Системный аналитик | **39** no_match | **10** no_match<br>Δ=-29, 1816ms | **32** no_match<br>Δ=-7, 1877ms |
| HRA-EVAL-000020 | Орлов Андрей Владимирович<br>(Врач) | Специалист по разметке данных | **27** no_match | **10** no_match<br>Δ=-17, 1968ms | **0** no_match<br>Δ=-27, 1965ms |

---

## Статистика по сегментам

### Borderline (30 пар)

| Метрика | Prompt A | Prompt B | Разница |
|--------|----------|----------|---------|
| **MAE** | 9.43 | 17.77 | +88.5% ❌ |
| **Avg Latency** | 1981 ms | 2415 ms | +21.9% |
| **Accuracy** | 93.3% (28/30) | 90.0% (27/30) | -3.3% |

### Obvious Match (30 пар)

| Метрика | Prompt A | Prompt B | Разница |
|--------|----------|----------|---------|
| **MAE** | 9.50 | 13.90 | +46.3% ❌ |
| **Avg Latency** | 2029 ms | 2126 ms | +4.8% |
| **Accuracy** | 93.3% (28/30) | 93.3% (28/30) | 0% |

### Obvious No-Match (30 пар)

| Метрика | Prompt A | Prompt B | Разница |
|--------|----------|----------|---------|
| **MAE** | 11.97 | 15.57 | +30.1% ❌ |
| **Avg Latency** | 2139 ms | 2182 ms | +2.0% |
| **Accuracy** | 100% (30/30) | 100% (30/30) | 0% |

---

## Ключевые наблюдения

1. **Prompt B систематически показывает бо́льшую ошибку (MAE)** на всех сегментах:
   - Borderline: +88.5% (17.77 vs 9.43)
   - Obvious Match: +46.3% (13.90 vs 9.50)
   - Obvious No-Match: +30.1% (15.57 vs 11.97)

2. **Prompt A точнее на borderline кейсах** — критичный сегмент для matching:
   - MAE: 9.43 vs 17.77
   - Accuracy: 93.3% vs 90.0%

3. **Оба промпта хорошо справляются с obvious_no_match** (accuracy 100%)

4. **Prompt B имеет бо́льший разброс latency** — особенно на borderline (+434ms)

5. **Prompt A выигрывает по всем метрикам** на всех трёх сегментах

---

*Таблица сгенерирована из Production PostgreSQL database 2026-06-28*