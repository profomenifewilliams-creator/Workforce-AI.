(function () {
  "use strict";

  var $ = function (selector, root) { return (root || document).querySelector(selector); };
  var $$ = function (selector, root) { return Array.prototype.slice.call((root || document).querySelectorAll(selector)); };

  var menuToggle = $("#menuToggle");
  var mainNav = $("#mainNav");
  if (menuToggle && mainNav) {
    menuToggle.addEventListener("click", function () {
      var opened = mainNav.classList.toggle("open");
      menuToggle.setAttribute("aria-expanded", opened ? "true" : "false");
      menuToggle.setAttribute("aria-label", opened ? "Close navigation" : "Open navigation");
    });
    $$(".nav-link", mainNav).forEach(function (link) {
      link.addEventListener("click", function () {
        mainNav.classList.remove("open");
        menuToggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  var lessonForm = $("#lessonForm");
  var topicInput = $("#topicInput");
  var lessonStatus = $("#lessonStatus");
  var lessonResult = $("#lessonResult");
  var ageGroup = $("#ageGroup");
  var language = $("#language");
  var learningStyle = $("#learningStyle");
  var activeLesson = null;
  var selectedAnswer = null;

  function escapeHTML(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, function (character) {
      return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[character];
    });
  }

  function readCookie(name) {
    var prefix = name + "=";
    var bits = document.cookie ? document.cookie.split(";") : [];
    for (var i = 0; i < bits.length; i += 1) {
      var bit = bits[i].trim();
      if (bit.indexOf(prefix) === 0) return decodeURIComponent(bit.substring(prefix.length));
    }
    return "";
  }

  function setStatus(message, tone) {
    lessonStatus.hidden = false;
    lessonStatus.className = "lesson-status" + (tone ? " " + tone : "");
    lessonStatus.textContent = message;
  }

  function hideStatus() {
    lessonStatus.hidden = true;
    lessonStatus.className = "lesson-status";
    lessonStatus.textContent = "";
  }

  function displayLesson(data) {
    var steps = Array.isArray(data.steps) ? data.steps.slice(0, 3) : [];
    var quiz = data.quiz || {};
    var options = Array.isArray(quiz.options) ? quiz.options.slice(0, 3) : [];
    var isAI = data.aiUsed === true || data.ai_used === true || data.mode === "ai";
    activeLesson = data;
    selectedAnswer = null;
    var html = "";
    html += '<span class="lesson-ai-tag">' + (isAI ? "✦ AI-GENERATED MINI LESSON" : "✦ GUIDED MINI LESSON") + '</span>';
    html += '<h3>' + escapeHTML(data.title || "Your mini lesson") + '</h3>';
    html += '<p>' + escapeHTML(data.intro || "Let's explore this idea together.") + '</p>';
    html += '<div class="lesson-steps">';
    steps.forEach(function (step, index) {
      html += '<div class="lesson-step"><span class="lesson-step-num">' + (index + 1) + '</span><div><strong>' + escapeHTML(step.title || "Explore the idea") + '</strong><p>' + escapeHTML(step.body || "") + '</p></div></div>';
    });
    html += '</div>';
    if (quiz.question && options.length) {
      html += '<div class="quiz-block"><h4>✨ Quick check: ' + escapeHTML(quiz.question) + '</h4><div class="quiz-options">';
      options.forEach(function (option, index) {
        html += '<button type="button" class="quiz-option" data-answer="' + index + '">' + escapeHTML(option) + '</button>';
      });
      html += '</div><p class="quiz-result" id="quizResult" hidden></p></div>';
    }
    if (data.challenge) {
      html += '<div class="challenge-block"><span>🚀</span><div><strong>Your mini challenge</strong><p>' + escapeHTML(data.challenge) + '</p></div></div>';
    }
    if (data.notice || data.error) {
      html += '<p class="lesson-disclaimer">' + escapeHTML(data.notice || data.error) + '</p>';
    }
    html += '<button type="button" class="lesson-reset" id="lessonReset">Ask another question ↗</button>';
    lessonResult.innerHTML = html;
    lessonResult.hidden = false;

    $$(".quiz-option", lessonResult).forEach(function (button) {
      button.addEventListener("click", function () {
        if (selectedAnswer !== null) return;
        selectedAnswer = Number(button.getAttribute("data-answer"));
        var correct = Number(quiz.correctIndex);
        $$(".quiz-option", lessonResult).forEach(function (option) {
          option.disabled = true;
          if (Number(option.getAttribute("data-answer")) === correct) option.classList.add("correct");
          if (option === button && selectedAnswer !== correct) option.classList.add("selected");
        });
        var result = $("#quizResult", lessonResult);
        if (result) {
          result.hidden = false;
          result.textContent = selectedAnswer === correct
            ? "Brilliant thinking! " + (quiz.explanation || "Your answer is correct.")
            : "Good try, explorer! " + (quiz.explanation || "Keep practising; learning grows with every try.");
        }
      });
    });
    var reset = $("#lessonReset", lessonResult);
    if (reset) reset.addEventListener("click", function () {
      topicInput.value = "";
      topicInput.focus();
      lessonResult.hidden = true;
      hideStatus();
    });
    if (window.innerWidth < 760) lessonResult.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  async function createLesson(event) {
    if (event) event.preventDefault();
    var topic = (topicInput.value || "").trim();
    if (topic.length < 2) {
      topicInput.focus();
      setStatus("Add a question or topic so Lumi knows where to begin.", "error");
      return;
    }
    if (topic.length > 300) {
      setStatus("That topic is a little long. Please keep it under 300 characters.", "error");
      return;
    }
    lessonResult.hidden = true;
    setStatus("Lumi is preparing your learning adventure…", "loading");
    var submitButton = $(".topic-submit");
    if (submitButton) {
      submitButton.disabled = true;
      submitButton.textContent = "…";
    }
    try {
      var response = await fetch("/api/lesson/", {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": readCookie("csrftoken")
        },
        body: JSON.stringify({
          topic: topic,
          age_group: ageGroup ? ageGroup.value : "7–9 years",
          language: language ? language.value : "English",
          style: learningStyle ? learningStyle.value : "Adventure game"
        })
      });
      var data = await response.json();
      if (!response.ok) throw new Error(data.error || "The learning studio is busy. Please try again.");
      hideStatus();
      displayLesson(data);
    } catch (error) {
      setStatus((error && error.message) || "Lumi couldn't reach the learning studio just now. Please try again.", "error");
    } finally {
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.textContent = "→";
      }
    }
  }

  if (lessonForm) lessonForm.addEventListener("submit", createLesson);

  function launchTopic(topic, shouldSubmit) {
    if (!topicInput) return;
    topicInput.value = topic;
    topicInput.focus({ preventScroll: true });
    $("#teach").scrollIntoView({ behavior: "smooth", block: "start" });
    if (shouldSubmit) {
      window.setTimeout(function () { createLesson(); }, 250);
    }
  }

  $$("[data-topic]").forEach(function (button) {
    button.addEventListener("click", function () {
      var topic = button.getAttribute("data-topic") || "";
      var doSubmit = button.classList.contains("tutor-link");
      launchTopic(topic, doSubmit);
    });
  });

  $$(".suggestion-chip").forEach(function (button) {
    button.addEventListener("click", function () {
      topicInput.value = button.getAttribute("data-topic") || "";
      topicInput.focus();
    });
  });

  var dialog = $("#infoDialog");
  var dialogContent = $("#dialogContent");
  function showDialog(title, body) {
    if (!dialog || !dialogContent) return;
    dialogContent.innerHTML = '<h2>' + escapeHTML(title) + '</h2>' + body;
    if (typeof dialog.showModal === "function") dialog.showModal();
    else dialog.setAttribute("open", "open");
    document.body.classList.add("dialog-open");
  }
  function closeDialog() {
    if (!dialog) return;
    if (typeof dialog.close === "function") dialog.close();
    else dialog.removeAttribute("open");
    document.body.classList.remove("dialog-open");
  }
  var dialogClose = $("#dialogClose");
  if (dialogClose) dialogClose.addEventListener("click", closeDialog);
  if (dialog) {
    dialog.addEventListener("click", function (event) {
      if (event.target === dialog) closeDialog();
    });
    dialog.addEventListener("close", function () { document.body.classList.remove("dialog-open"); });
  }

  var showJourney = $("#showJourney");
  if (showJourney) showJourney.addEventListener("click", function () {
    showDialog("Welcome to your learning universe!", '<p>Every question can become an adventure. Choose a subject, meet a friendly guide, and try a short activity that helps you understand the idea.</p><ul><li>Explore the subject cards and choose what sparks your curiosity.</li><li>Ask Lumi to build a mini lesson just for your chosen topic.</li><li>Try the quick games and check your answer to see what you learned.</li></ul><a class="button button-primary" href="#subjects" id="dialogStart">Explore the subjects →</a>');
    var start = $("#dialogStart");
    if (start) start.addEventListener("click", closeDialog);
  });

  var safetyDetails = $("#safetyDetails");
  if (safetyDetails) safetyDetails.addEventListener("click", function () {
    showDialog("A safe space to grow", '<p>AfriLearn AI is being built around children’s wellbeing, appropriate learning and family involvement.</p><ul><li>Keep lesson questions educational and age-aware.</li><li>Do not share personal information in a learning prompt.</li><li>AI-generated material can be wrong; check important facts with a trusted adult or teacher.</li><li>The lesson preview does not store submitted prompts as learning records.</li><li>Parent accounts, guardian acknowledgement and saved child progress need full deployment testing before public family accounts are introduced.</li></ul>');
  });

  var headerBell = $("#headerBell");
  if (headerBell) headerBell.addEventListener("click", function () {
    showDialog("Today's little big mission", '<p><strong>Mission: Ask a brilliant question.</strong></p><p>Choose one thing you have always wondered about, learn three new facts, and explain one of them in your own words.</p><p>Mission reward: a very proud brain and one new discovery. ✨</p><button class="button button-primary" id="missionStart" type="button">Start my mission →</button>');
    var start = $("#missionStart");
    if (start) start.addEventListener("click", function () { closeDialog(); launchTopic("Why do stars shine?", false); });
  });

  var searchOpen = $("#searchOpen");
  if (searchOpen) searchOpen.addEventListener("click", function () {
    showDialog("What are you curious about?", '<p>Choose a starter question, or write your own one in the lesson builder.</p><div class="game-answer-row"><button class="game-answer" data-search-topic="How do volcanoes work?">🌋 Volcanoes</button><button class="game-answer" data-search-topic="How do computers think?">💻 Computers</button><button class="game-answer" data-search-topic="Why do plants need sunlight?">🌱 Plants</button><button class="game-answer" data-search-topic="Tell me about the African continent">🌍 Africa</button></div>');
    $$("[data-search-topic]").forEach(function (button) {
      button.addEventListener("click", function () { var topic = button.getAttribute("data-search-topic"); closeDialog(); launchTopic(topic, false); });
    });
  });

  $$(".language-pills button").forEach(function (button) {
    button.addEventListener("click", function () {
      var languageName = button.getAttribute("data-language") || "Igbo";
      if (language) language.value = languageName;
      launchTopic("Teach me a friendly greeting in " + languageName, true);
    });
  });

  var games = {
    quickMath: {
      title: "Number Quest",
      intro: "A basket has 3 mangoes. You pick up 2 more. How many mangoes are in the basket now?",
      answers: ["4 mangoes", "5 mangoes", "6 mangoes"],
      correct: 1,
      explain: "3 + 2 = 5. You added two mangoes to the three already there. Nice counting!"
    },
    quickWord: {
      title: "Word Garden",
      intro: "Which word means a place where many books can be found and borrowed?",
      answers: ["Library", "Stadium", "Airport"],
      correct: 0,
      explain: "A library is a place to read, discover and borrow books. Words open worlds!"
    },
    quickScience: {
      title: "Science Snap",
      intro: "What gives most plants the energy they need to grow?",
      answers: ["Moonlight only", "Sunlight", "Sand alone"],
      correct: 1,
      explain: "Plants use energy from sunlight to make their own food. Nature is full of clever ideas!"
    }
  };
  Object.keys(games).forEach(function (id) {
    var button = $("#" + id);
    if (!button) return;
    button.addEventListener("click", function () { showGame(games[id]); });
  });

  function showGame(game) {
    var choices = game.answers.map(function (answer, index) {
      return '<button type="button" class="game-answer" data-game-answer="' + index + '">' + escapeHTML(answer) + '</button>';
    }).join("");
    var target = $("#gameChallenge");
    target.innerHTML = '<strong>' + escapeHTML(game.title) + '</strong><p>' + escapeHTML(game.intro) + '</p><div class="game-answer-row">' + choices + '</div><p id="gameFeedback" class="quiz-result" hidden></p>';
    target.hidden = false;
    $$("[data-game-answer]", target).forEach(function (answerButton) {
      answerButton.addEventListener("click", function () {
        $$("[data-game-answer]", target).forEach(function (item) { item.disabled = true; });
        var chosen = Number(answerButton.getAttribute("data-game-answer"));
        answerButton.classList.add(chosen === game.correct ? "correct" : "selected");
        var feedback = $("#gameFeedback", target);
        feedback.hidden = false;
        feedback.textContent = (chosen === game.correct ? "Brilliant! " : "Good try! ") + game.explain;
      });
    });
    target.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  document.addEventListener("keydown", function (event) {
    if (event.key === "/" && !/input|textarea|select/i.test(document.activeElement && document.activeElement.tagName || "")) {
      event.preventDefault();
      launchTopic("", false);
    }
    if (event.key === "Escape") closeDialog();
  });

  // Keep the dashboard feeling alive without storing children's activity.
  var subjectCards = $$(".subject-card");
  subjectCards.forEach(function (card) {
    card.addEventListener("keydown", function (event) {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        launchTopic(card.getAttribute("data-topic") || "", false);
      }
    });
  });
})();
