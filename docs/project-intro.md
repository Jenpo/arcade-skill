# Arcade Skill Project Intro

Ready-to-use project descriptions for GitHub, launch posts, directories, and landing pages.

## 中文

### 一句话

Arcade Skill 是给 Claude Code / Codex 等 AI 编程工具准备的浏览器小游戏技能：当 agent 在安装依赖、跑测试、重构代码时，你可以一句话打开一把《是男人就下100层》。

### 短介绍

Arcade Skill 把轻量街机小游戏装进 AI 开发工作流。它不是把游戏塞进技能包，而是用一个极薄的 Python 加载器读取远程 manifest，校验单文件 HTML bundle 的 sha256，然后在本地浏览器打开游戏。游戏内容、公告、开关和后续新增游戏都可以热更新，用户安装一次即可持续收到新版本。

### 长介绍

AI 编程时代有很多等待碎片：安装依赖、运行测试、生成代码、部署预览。Arcade Skill 把这些 30 秒到 5 分钟的空档变成一把即开即玩的街机小游戏。

M1 首发游戏是自研重写的《Down 100 Floors / 是男人就下100层》：左右移动、下落平台、躲避尖刺、刷新层数纪录。项目采用薄壳热更新架构，已安装技能只负责拉取 manifest、验证哈希、本地缓存和打开浏览器；真正的游戏内容托管在 `arcade.fxpeek.com`，后续新增游戏、公告、打赏入口、广告开关和紧急下架都只需要修改远程 JSON 或 bundle。

### 游戏背景与玩法

《Down 100 Floors / 是男人就下100层》来自早期网页和手机街机小游戏的经典玩法谱系：玩家不是向上闯关，而是在不断上升的天花板压力下向下逃生。屏幕里的平台会持续上移，你必须左右移动，准确落到下一层平台，避开尖刺和危险板，尽可能下到更深的层数。

挑战的核心很简单：**活得越久，下得越深，排名越高**。普通平台可以让你稳定落脚并回复血量；尖刺会扣血；弹簧平台会把你弹起；移动平台和脆弱平台会打乱节奏。游戏的紧张感来自两个方向：上方天花板不断逼近，下方平台又要求你快速判断落点。

过去这类玩法的魅力在于“一局很短，但总想再来一次”。它适合排队、课间、摸鱼，也非常适合 AI agent 正在跑任务时的等待时间。Arcade Skill 版本保留了这种低学习成本、高重开率的节奏，同时使用全新代码和自制像素风视觉，避免使用任何原站代码或素材。

### 排名与公平性

当前版本记录本地个人最佳层数。后续全球排行榜上线时，排行榜模式会坚持同一套公平规则：相同血量、无付费加成、无买命、无强度优势。休闲玩法可以更爽，但排行榜必须保持纯技巧比较。

排名建议口径：

- 主要排名：最深层数。
- 同层数加权：用时更短者优先。
- 作弊防护：上传成绩时记录版本号、模式、随机种子和关键事件摘要。
- 分享文案：破纪录或游戏结束时复制文本战绩，带 `?ref=share` 用于统计传播。

## English

### One-liner

Arcade Skill launches tiny browser arcade games while Claude Code, Codex, or another coding agent is busy working.

### Short Description

Arcade Skill is a hot-updated mini-game launcher for AI coding workflows. Install the skill once, then say “I’m bored” or “play a game” while your agent runs tests, installs dependencies, or refactors code. A lightweight Python launcher fetches a remote manifest, verifies each HTML bundle with sha256, caches it locally, and opens the game in your browser.

### Long Description

Coding agents create a new kind of waiting time: a test suite is running, a dependency tree is installing, a refactor is being generated, or a deployment is building. Arcade Skill turns those idle moments into a quick arcade break.

The first game is a clean-room rewrite of **Down 100 Floors**: move left and right, land on platforms, avoid spikes, and chase a new personal best. The installed skill stays thin and stable; game content lives behind a remote manifest on `arcade.fxpeek.com`. New games, announcements, tip links, monetization switches, and emergency kill switches can ship through hot updates without asking users to reinstall.

### Game Background and Gameplay

**Down 100 Floors** belongs to the classic family of early web and mobile arcade games where the goal is not to climb upward, but to survive by descending. The platforms scroll upward, the ceiling keeps closing in, and the player has to move left or right to land safely on the next platform.

The challenge is direct: **survive longer, descend deeper, rank higher**. Normal platforms give you a stable landing and can restore health. Spikes deal damage. Springs launch you upward. Moving and fragile platforms break your rhythm. The pressure comes from both sides: the ceiling punishes hesitation, while the next landing demands timing.

The original appeal of this genre was always “one more try”: each run is short, failure is immediate, and improvement feels visible. That makes it a strong fit for idle moments while an AI coding agent is running tests, installing dependencies, or generating code. This version is a clean-room implementation with original pixel-style visuals and no third-party game code or art.

### Ranking and Fair Play

The current release stores a local personal best. When global leaderboards ship, ranked mode should stay skill-pure: same health, no paid power, no paid revives, and no advantage that changes the competitive rules. Casual mode can be more forgiving, but ranked mode must remain fair.

Suggested ranking rules:

- Primary rank: deepest floor reached.
- Tie-breaker: faster time wins at the same floor.
- Anti-cheat metadata: submit game version, mode, random seed, and a compact event summary.
- Sharing loop: game-over and new-best states copy a text score with `?ref=share` for attribution.

## Français

### Phrase courte

Arcade Skill lance de petits jeux d’arcade dans le navigateur pendant que Claude Code, Codex ou un autre agent de développement travaille.

### Description courte

Arcade Skill est un lanceur de mini-jeux pensé pour les temps morts du développement assisté par IA. Installez le skill une seule fois, puis demandez à jouer pendant que votre agent installe des dépendances, exécute des tests ou génère du code. Le chargeur Python récupère un manifest distant, vérifie le hash sha256 du bundle HTML, le met en cache localement et ouvre le jeu dans le navigateur.

### Description longue

Les agents de programmation créent de nouveaux moments d’attente : tests en cours, dépendances en installation, refactorisation automatique, build ou déploiement. Arcade Skill transforme ces pauses de 30 secondes à quelques minutes en une partie rapide.

Le premier jeu est une réécriture originale de **Down 100 Floors** : se déplacer à gauche ou à droite, tomber de plateforme en plateforme, éviter les pièges et battre son record. Le skill installé reste minimal ; le contenu des jeux est distribué via un manifest distant sur `arcade.fxpeek.com`, ce qui permet d’ajouter des jeux, de modifier les annonces ou de couper une version problématique sans réinstallation.

### Contexte du jeu et règles

**Down 100 Floors** s’inscrit dans la lignée des anciens jeux d’arcade web et mobile : il ne faut pas monter, mais descendre pour survivre. Les plateformes remontent, le plafond se rapproche, et le joueur doit se déplacer à gauche ou à droite pour atterrir sur la prochaine plateforme.

Le défi est simple : **survivre plus longtemps, descendre plus bas, obtenir un meilleur classement**. Les plateformes normales permettent de reprendre le rythme et de récupérer de la vie. Les pics infligent des dégâts. Les ressorts propulsent le joueur. Les plateformes mobiles ou fragiles perturbent la trajectoire.

Ce type de jeu fonctionne parce qu’une partie est courte et donne immédiatement envie de recommencer. Il convient donc très bien aux petites pauses pendant qu’un agent IA exécute des tests, installe des dépendances ou génère du code. Cette version utilise un code original et des visuels pixel créés pour le projet.

### Classement et équité

La version actuelle conserve le meilleur score local. Lorsqu’un classement global sera ajouté, le mode classé devra rester équitable : mêmes points de vie, aucun bonus payant, aucune résurrection payante, aucune mécanique qui donne un avantage compétitif.

Règles recommandées :

- Classement principal : profondeur maximale atteinte.
- Égalité : le temps le plus court l’emporte.
- Anti-triche : envoyer la version, le mode, la graine aléatoire et un résumé d’événements.
- Partage : le score copié contient `?ref=share` pour mesurer la propagation.

## Italiano

### Frase breve

Arcade Skill apre piccoli giochi arcade nel browser mentre Claude Code, Codex o un altro agente di coding sta lavorando.

### Descrizione breve

Arcade Skill è un launcher di mini-giochi per i tempi morti del coding assistito dall’AI. Lo installi una volta, poi puoi chiedere di giocare mentre l’agente esegue test, installa dipendenze o genera codice. Il launcher Python scarica un manifest remoto, verifica il bundle HTML con sha256, lo salva in cache e apre il gioco nel browser.

### Descrizione lunga

Gli agenti di sviluppo creano nuovi momenti di attesa: test in esecuzione, dipendenze in installazione, refactor automatici, build e deploy. Arcade Skill trasforma questi intervalli in una partita arcade immediata.

Il primo gioco è una riscrittura originale di **Down 100 Floors**: muoviti a sinistra e a destra, atterra sulle piattaforme, evita le spine e prova a battere il tuo record. Lo skill installato rimane leggero e stabile; i contenuti vengono distribuiti tramite un manifest remoto su `arcade.fxpeek.com`, così nuovi giochi, avvisi, link di supporto e kill switch possono essere aggiornati senza reinstallare nulla.

### Contesto e gameplay

**Down 100 Floors** appartiene alla tradizione dei vecchi giochi arcade web e mobile: non bisogna salire, ma scendere per sopravvivere. Le piattaforme scorrono verso l’alto, il soffitto si avvicina e il giocatore deve muoversi a sinistra o a destra per atterrare in sicurezza.

La sfida è chiara: **sopravvivi più a lungo, scendi più in basso, ottieni un punteggio migliore**. Le piattaforme normali stabilizzano il ritmo e possono recuperare vita. Le spine infliggono danno. Le molle ti lanciano verso l’alto. Le piattaforme mobili e fragili rompono il tempo di gioco.

Il fascino storico di questo genere è il ciclo “ancora una partita”: le sessioni sono brevi, l’errore è immediato e il miglioramento si sente subito. Per questo funziona bene durante le attese generate dagli agenti AI. Questa versione è una riscrittura pulita, con codice e grafica originali.

### Classifica e fair play

La versione attuale salva il record personale locale. Quando arriverà la classifica globale, la modalità classificata dovrà restare equa: stessa vita per tutti, nessun potenziamento a pagamento, nessuna resurrezione a pagamento e nessun vantaggio competitivo.

Regole consigliate:

- Classifica principale: piano più profondo raggiunto.
- Spareggio: a parità di piano vince il tempo migliore.
- Anti-cheat: inviare versione, modalità, seed casuale e riepilogo eventi.
- Condivisione: il testo copiato include `?ref=share` per misurare la diffusione.

## العربية

### جملة قصيرة

Arcade Skill يفتح ألعاب أركيد صغيرة في المتصفح أثناء عمل Claude Code أو Codex أو أي وكيل برمجة آخر.

### وصف قصير

Arcade Skill هو مشغل ألعاب خفيفة مخصص لفترات الانتظار أثناء البرمجة بمساعدة الذكاء الاصطناعي. تثبته مرة واحدة، ثم تطلب تشغيل لعبة عندما يكون الوكيل مشغولاً بتثبيت الحزم أو تشغيل الاختبارات أو إعادة هيكلة الكود. يقوم مشغل Python بقراءة manifest بعيد، والتحقق من حزمة HTML عبر sha256، وتخزينها محلياً، ثم فتح اللعبة في المتصفح.

### وصف طويل

أدوات البرمجة بالذكاء الاصطناعي تخلق لحظات انتظار جديدة: اختبار يعمل، حزم يتم تثبيتها، كود يتم توليده، أو نشر قيد التنفيذ. Arcade Skill يحول هذه الفواصل القصيرة إلى لعبة أركيد سريعة.

اللعبة الأولى هي إعادة كتابة أصلية للعبة **Down 100 Floors**: تحرك يميناً ويساراً، اهبط على المنصات، تجنب الأشواك، وحاول تسجيل رقم قياسي جديد. يبقى skill المثبت خفيفاً وثابتاً، بينما يتم تحديث الألعاب والملاحظات والروابط ومفاتيح الإيقاف عبر manifest بعيد على `arcade.fxpeek.com` دون حاجة المستخدمين لإعادة التثبيت.

### خلفية اللعبة وطريقة اللعب

تنتمي **Down 100 Floors** إلى نوع كلاسيكي من ألعاب الويب والهواتف القديمة: الهدف ليس الصعود، بل الهبوط والبقاء على قيد الحياة. تتحرك المنصات إلى أعلى، ويقترب السقف، وعلى اللاعب التحرك يميناً ويساراً للهبوط على المنصة التالية بأمان.

التحدي واضح: **ابقَ أطول، اهبط أعمق، واحصل على ترتيب أعلى**. المنصات العادية تمنح هبوطاً آمناً وقد تعيد بعض الصحة. الأشواك تسبب ضرراً. النوابض تقذف اللاعب إلى أعلى. المنصات المتحركة والهشة تكسر الإيقاع وتجعل القرار أسرع.

سحر هذا النوع من الألعاب أنه قصير وسريع ويجعلك تقول: محاولة أخرى. لذلك يناسب فترات الانتظار أثناء عمل وكيل البرمجة بالذكاء الاصطناعي. هذه النسخة مكتوبة من الصفر، برسوم بسيطة أصلية، ولا تستخدم كوداً أو أصولاً من ألعاب أخرى.

### الترتيب والعدالة

الإصدار الحالي يحفظ أفضل نتيجة محلية. عند إطلاق لوحة ترتيب عالمية، يجب أن تبقى المنافسة عادلة: نفس الصحة للجميع، لا مزايا مدفوعة، لا إحياء مدفوع، ولا أي قوة إضافية تغيّر قواعد المنافسة.

قواعد الترتيب المقترحة:

- الترتيب الأساسي: أعمق طابق يصل إليه اللاعب.
- كسر التعادل: الوقت الأسرع عند نفس الطابق.
- مكافحة الغش: إرسال نسخة اللعبة، وضع اللعب، seed العشوائي، وملخص أحداث مختصر.
- المشاركة: نص النتيجة يحتوي على `?ref=share` لقياس الانتشار.

## Positioning Tags

- AI coding break
- Browser mini-game
- Claude Code skill
- Codex companion
- Hot-updated HTML game bundle
- Down 100 Floors
- Agent-era loading screen
