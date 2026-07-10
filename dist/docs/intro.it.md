# Arcade Skill

[中文](intro.zh.md) · [English](intro.en.md) · [Français](intro.fr.md) · [Italiano](intro.it.md) · [العربية](intro.ar.md)

## Frase breve

Arcade Skill apre piccoli giochi arcade nostalgici nel browser mentre Claude Code, Codex o un altro agente di coding compila, testa o pensa molto intensamente.

## Descrizione breve

Arcade Skill è un launcher di mini-giochi per i tempi morti del coding assistito dall’AI. Lo installi una volta, poi puoi chiedere di giocare mentre l’agente esegue test, installa dipendenze o genera codice. Il launcher Python scarica un manifest remoto, verifica il bundle HTML autonomo con sha256, lo salva in cache e apre il gioco nel browser. Il sapore è metà utility da terminale, metà sala giochi del vecchio web.

## Descrizione lunga

Gli agenti di sviluppo creano nuovi momenti di attesa: test in esecuzione, dipendenze in installazione, refactor automatici, build e deploy. Arcade Skill trasforma questi intervalli in un piccolo giocattolo da sviluppatore: URL locale, log del manifest, bundle verificato e una partita che parte prima che tu apra un’altra scheda per noia.

Il primo gioco è una riscrittura originale di **Down 100 Floors**: muoviti a sinistra e a destra, atterra sulle piattaforme, evita le spine e prova a battere il tuo record. Lo skill installato rimane leggero e stabile; i contenuti vengono distribuiti tramite un manifest remoto su `arcade.fxpeek.com`, così nuovi giochi, avvisi, link di supporto e kill switch possono essere aggiornati senza reinstallare nulla.

## Contesto e gameplay

**Down 100 Floors** appartiene alla tradizione dei vecchi giochi arcade web, Flash e mobile: non bisogna salire, ma scendere per sopravvivere. Le piattaforme scorrono verso l’alto, il soffitto si avvicina e il giocatore deve muoversi a sinistra o a destra per atterrare in sicurezza.

La sfida è chiara: **sopravvivi più a lungo, scendi più in basso, ottieni un punteggio migliore**. Le piattaforme normali stabilizzano il ritmo e possono recuperare vita. Le spine infliggono danno. Le molle ti lanciano verso l’alto. Le piattaforme mobili e fragili rompono il tempo di gioco.

Il fascino storico di questo genere è il ciclo “ancora una partita”: le sessioni sono brevi, l’errore è immediato e il miglioramento si sente subito. Per questo funziona bene durante le attese generate dagli agenti AI. Questa versione conserva quel ciclo nostalgico, ma usa codice e grafica originali.

## Classifica e fair play

La versione attuale salva il record personale locale. Quando arriverà la classifica globale, la modalità classificata dovrà restare equa: stessa vita per tutti, nessun potenziamento a pagamento, nessuna resurrezione a pagamento e nessun vantaggio competitivo.

- Classifica principale: piano più profondo raggiunto.
- Spareggio: a parità di piano vince il tempo migliore.
- Anti-cheat: inviare versione, modalità, seed casuale e riepilogo eventi.
- Condivisione: il testo copiato include `?ref=share` per misurare la diffusione.
