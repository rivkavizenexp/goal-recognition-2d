/** (July 2012, Erik Weitnauer)
The html-plugin will load and display an external html pages. To proceed to the next, the
user might either press a button on the page or a specific key. Afterwards, the page get hidden and
the plugin will wait of a specified time before it proceeds.

documentation: docs.jspsych.org
*/

jsPsych.plugins['external-html'] = (function() {

    var plugin = {};
  
    plugin.info = {
      name: 'external-html',
      description: '',
      parameters: {
        url: {
          type: jsPsych.plugins.parameterType.STRING,
          pretty_name: 'URL',
          default: undefined,
          description: 'The url of the external html page'
        },
        cont_key: {
          type: jsPsych.plugins.parameterType.KEYCODE,
          pretty_name: 'Continue key',
          default: null,
          description: 'The key to continue to the next page.'
        },
        cont_btn: {
          type: jsPsych.plugins.parameterType.STRING,
          pretty_name: 'Continue button',
          default: null,
          description: 'The button to continue to the next page.'
        },
        check_fn: {
          type: jsPsych.plugins.parameterType.FUNCTION,
          pretty_name: 'Check function',
          default: function() {return true},
          description: ''
        },
        force_refresh: {
          type: jsPsych.plugins.parameterType.BOOL,
          pretty_name: 'Force refresh',
          default: false,
          description: 'Refresh page.'
        },
        // if execute_Script == true, then all javascript code on the external page
        // will be executed in the plugin site within your jsPsych test
        execute_script: {
          type: jsPsych.plugins.parameterType.BOOL,
          pretty_name: 'Execute scripts',
          default: false,
          description: 'If true, JS scripts on the external html file will be executed.'
        },
        on_submit_form: {
          type: jsPsych.plugins.parameterType.FUNCTION,
          pretty_name: 'On submit finction',
          default: ()=> {return true},
          description: 'function to execute on form submission'

        }
      }
    }
  
    plugin.trial = function(display_element, trial) {
  
      var url = trial.url;
      if (trial.force_refresh) {
        url = trial.url + "?t=" + performance.now();
      }
  
      load(display_element, url, function() {
        var t0 = performance.now();
        var finish = function() {
          if (trial.check_fn && !trial.check_fn(display_element)) { return };
          if (trial.cont_key) { display_element.removeEventListener('keydown', key_listener); }
          var trial_data = {
            rt: performance.now() - t0,
            url: trial.url
          };
          display_element.innerHTML = '';
          jsPsych.finishTrial(trial_data);
        };
  
        // by default, scripts on the external page are not executed with XMLHttpRequest().
        // To activate their content through DOM manipulation, we need to relocate all script tags
        if (trial.execute_script) {
          for (const scriptElement of display_element.getElementsByTagName("script")) {
          const relocatedScript = document.createElement("script");
          relocatedScript.text = scriptElement.text;
          if(scriptElement.hasAttribute('src'))
            relocatedScript.src = scriptElement.src;
          scriptElement.parentNode.replaceChild(relocatedScript, scriptElement);
          };
        }
  
        if (trial.cont_btn) { display_element.querySelector('#'+trial.cont_btn).addEventListener('click', finish); }
        if (trial.cont_key) {
          var key_listener = function(e) {
            if (e.which == trial.cont_key) finish();
          };
          display_element.addEventListener('keydown', key_listener);
        }

        if(trial.on_submit_form){
          let onSubmit = function(event){
            // don't submit form
            event.preventDefault();

            // measure response time
            var endTime = performance.now();
            var response_time = endTime - startTime;

            var question_data = serializeArray(this);

            trial.on_submit_form(question_data)

            // save data
            var trialdata = {
              "rt": response_time,
              "responses": JSON.stringify(question_data)
            };

            display_element.innerHTML = '';

            // next trial
            jsPsych.finishTrial(trialdata);

          }

          for (const formElement of display_element.getElementsByTagName("form")) {
            const relocatedScript = document.createElement("form");
            relocatedScript.innerHTML = formElement.innerHTML;
            relocatedScript.addEventListener('submit',onSubmit);
            formElement.parentNode.replaceChild(relocatedScript, formElement);
          }
        }
        var startTime = performance.now();
      });
    };
  
  /*!
   * Serialize all form data into an array
   * (c) 2018 Chris Ferdinandi, MIT License, https://gomakethings.com
   * @param  {Node}   form The form to serialize
   * @return {String}      The serialized form data
   */
  var serializeArray = function (form) {
    // Setup our serialized data
    var serialized = [];

    // Loop through each field in the form
    for (var i = 0; i < form.elements.length; i++) {
      var field = form.elements[i];

      // Don't serialize fields without a name, submits, buttons, file and reset inputs, and disabled fields
      if (!field.name || field.disabled || field.type === 'file' || field.type === 'reset' || field.type === 'submit' || field.type === 'button') continue;

      // If a multi-select, get all selections
      if (field.type === 'select-multiple') {
        for (var n = 0; n < field.options.length; n++) {
          if (!field.options[n].selected) continue;
          serialized.push({
            name: field.name,
            value: field.options[n].value
          });
        }
      }

      // Convert field data to a query string
      else if ((field.type !== 'checkbox' && field.type !== 'radio') || field.checked) {
        serialized.push({
          name: field.name,
          value: field.value
        });
      }
    }

    return serialized;
  };


    // helper to load via XMLHttpRequest
    function load(element, file, callback){
      var xmlhttp = new XMLHttpRequest();
      xmlhttp.open("GET", file, true);
      xmlhttp.onload = function(){
          if(xmlhttp.status == 200 || xmlhttp.status == 0){ //Check if loaded
              element.innerHTML = xmlhttp.responseText;
              callback();
          }
      }
      xmlhttp.send();
    }
  
    return plugin;
  })();