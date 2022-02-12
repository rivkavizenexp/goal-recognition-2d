/**
 * jspsych-free-sort
 * plugin for drag-and-drop sorting of a collection of images
 * Josh de Leeuw
 *
 * documentation: docs.jspsych.org
 */


jsPsych.plugins['free-sort'] = (function() {

  var plugin = {};

  plugin.info = {
    name: 'free-sort',
    description: '',
    parameters: {
      stim_path: {
        type: jsPsych.plugins.parameterType.STRING,
        pretty_name: 'Stimuli path',
        default: undefined,
        description: 'Path of stimuli'
      },
      stim_id: {
        type: jsPsych.plugins.parameterType.STRING,
        pretty_name: 'Stimuli ID',
        default: undefined,
        description: 'ID of stimuli'
      },
      prompt: {
        type: jsPsych.plugins.parameterType.STRING,
        pretty_name: 'Prompt',
        default: null,
        description: 'It can be used to provide a reminder about the action the subject is supposed to take.'
      },
      prompt_location: {
        type: jsPsych.plugins.parameterType.SELECT,
        pretty_name: 'Prompt location',
        options: ['above','below'],
        default: 'above',
        description: 'Indicates whether to show prompt "above" or "below" the sorting area.'
      },
      button_label: {
        type: jsPsych.plugins.parameterType.STRING,
        pretty_name: 'Button label',
        default:  'Continue',
        description: 'The text that appears on the button to continue to the next trial.'
      },
      min_time: {
        type: jsPsych.plugins.parameterType.INT,
        pretty_name: 'Minimum Time',
        default:  0,
        description: 'the period to disable the contunue button.'
      }

    }
  };

  plugin.trial = function(display_element, trial) {

    var start_time = performance.now();

    var html = "";
    // check if there is a prompt and if it is shown above
    if (trial.prompt !== null && trial.prompt_location === "above") {
      html += trial.prompt;
    }

    html += '<div '+
      'id="jspsych-free-sort-arena" '+
      'class="jspsych-free-sort-arena" '+
      'style="position: relative; border:2px solid #444;"'+
      '></div>';

    // check if prompt exists and if it is shown below
    if (trial.prompt !== null && trial.prompt_location === "below") {
      html += trial.prompt;
    }

    display_element.innerHTML = html;
    var is_svg_onload_ran = false;

    let ajax = new XMLHttpRequest();
    ajax.open("GET", trial.stim_path, true);
    ajax.onload = function(e) {
      var svg_div = document.createElement("div");
      svg_div.innerHTML = ajax.responseText;
      svg_div.id = trial.stim_id;
      svg_div.className = "test-img";
      let svg_element = svg_div.children[0];
      svg_element.onload = onLoadFunc;
      let arena = display_element.querySelector("#jspsych-free-sort-arena");
      arena.appendChild(svg_div);

      // Make sure we are initializing the SVG - in case it loaded already
      if (!is_svg_onload_ran){
        svgInit(svg_element);
      }
    };
    ajax.send();

    // store initial location data
    var init_locations = [];

    display_element.innerHTML += '<button id="jspsych-free-sort-done-btn" class="jspsych-btn">'+trial.button_label+'</button>';
    
    //disable sort-done button for 5 seconds
    display_element.querySelector('#jspsych-free-sort-done-btn').disabled=true
    setTimeout(function(){
      display_element.querySelector('#jspsych-free-sort-done-btn').disabled=false
    },trial.min_time)
    
    var moves = [];
    var relative_moves = [];

    function onLoadFunc(evt){
      let svgDocument = evt.target;
      
      svgInit(svgDocument)

    }

    function svgInit(svgDocument){
      is_svg_onload_ran = true;


      let svg_child_nodes = svgDocument.children;
      
      var dynamic = svgDocument.getElementById("dynamic");
      for (let element of dynamic.children)
        element.classList.add("static")



      setTimeout(function(){
          for (let chiled of svg_child_nodes){
            if (chiled.id === "") { continue;}
    
            var bounding_rect = chiled.getBoundingClientRect();
    
            init_locations.push({
              "src": chiled.id,
              "x": bounding_rect.x,
              "y": bounding_rect.y
            });
          }

          for (let element of dynamic.children)
            element.classList.remove("static")

          
          makeDraggable(svgDocument);
      },5000)
    }

    function makeDraggable(svg){
      //make draggable
      svg.addEventListener('mousedown', startDrag);
      svg.addEventListener('mousemove', drag);
      svg.addEventListener('mouseup', endDrag);
      svg.addEventListener('mouseleave', endDrag);
      svg.addEventListener('touchstart', startDrag);
      svg.addEventListener('touchmove', drag);
      svg.addEventListener('touchend', endDrag);
      svg.addEventListener('touchleave', endDrag);
      svg.addEventListener('touchcancel', endDrag);

      var dynamic = svg.getElementById("dynamic");
      for (let element of dynamic.children)
        element.classList.add("draggable")

      var rect = dynamic.getBoundingClientRect()
      var x_init = rect.x;
      var y_init = rect.x;

      function getMousePosition(evt) {
        var CTM = svg.getScreenCTM();
        if (evt.touches) { evt = evt.touches[0]; }
        return {
          x: (evt.clientX - CTM.e) / CTM.a,
          y: (evt.clientY - CTM.f) / CTM.d
        };
      }

      var selectedElement, offset, transform;
      function startDrag(evt) {
        if (evt.target.classList.contains('draggable')) {
          selectedElement = evt.target;
          offset = getMousePosition(evt);
          // Make sure the first transform on the element is a translate transform
          var transforms = selectedElement.transform.baseVal;
          if (transforms.length === 0 || transforms.getItem(0).type !== SVGTransform.SVG_TRANSFORM_TRANSLATE) {
            // Create an transform that translates by (0, 0)
            var translate = svg.createSVGTransform();
            translate.setTranslate(0, 0);
            selectedElement.transform.baseVal.insertItemBefore(translate, 0);
          }
          // Get initial translation
          transform = transforms.getItem(0);
          offset.x -= transform.matrix.e;
          offset.y -= transform.matrix.f;
        }
      }

      function drag(evt) {
        if (selectedElement) {
          evt.preventDefault();
          var coord = getMousePosition(evt);
          transform.setTranslate(coord.x - offset.x, coord.y - offset.y);

          moves.push({
            "src": "dynamic",
            "x": coord.x,
            "y": coord.y
          });
          relative_moves.push({
            "src": "dynamic",
            "x": coord.x - x_init,
            "y": coord.y - y_init
          })

        }
      }
      function endDrag(evt) {
        selectedElement = false;
      }
    }

    // function makeDraggable(svg) {
    //   var rect = svg.getBoundingClientRect();
    //   svg.addEventListener('mousedown', startDrag);
    //   svg.addEventListener('mousemove', drag);
    //   svg.addEventListener('mouseup', endDrag);
    //   svg.addEventListener('mouseleave', endDrag);
    //   console.log("MAKE DRAGABLE")

    //   var selectedElement = false;

    //   var x = rect.x + 0.5 * rect.width;
    //   var y = rect.y + 0.5 * rect.height;

    //   function startDrag(e) {
    //     selectedElement = e.currentTarget;
    //     console.log("START DRAG")
    //   }

    //   function drag(e) {
    //     if (selectedElement) {
    //       e.preventDefault();

  
    //       let x_cor = (e.clientX - x) + 'px';
    //       let y_cor =  (e.clientY - y) + 'px';

    //       selectedElement.setAttributeNS(null, "x", x_cor);
    //       selectedElement.setAttributeNS(null, "y", y_cor);

    //       moves.push({
    //         "src": "dynamic",
    //         "x": e.clientX,
    //         "y": e.clientY
    //       });
    //       relative_moves.push({
    //         "src": "dynamic",
    //         "x": x_cor,
    //         "y": y_cor
    //       })
    //     }
    //   }

    //   function endDrag(e) {
    //     selectedElement = false;
    //     console.log("END DRAG")

    //   }
    // }

    display_element.querySelector('#jspsych-free-sort-done-btn').addEventListener('click', function(){

      var end_time = performance.now();
      var rt = end_time - start_time;
      // gather data
      // get final position of all objects
      var final_locations = [];
      let svg_element = display_element.querySelectorAll('.test-img')[0].firstElementChild;
      let dynamic = svg_element.getElementById("dynamic");
      let rect = dynamic.getBoundingClientRect();
      final_locations.push({
        "src": dynamic.id,
        "x": rect.x,
        "y": rect.y
      });

      var trial_data = {
        "stim_id": JSON.stringify(trial.stim_id),
        "init_locations": JSON.stringify(init_locations),
        "moves": JSON.stringify(moves),
        "relative moves": JSON.stringify(relative_moves),
        "final_locations": JSON.stringify(final_locations),
        "rt": rt
      };

      // advance to next part
      display_element.innerHTML = '';
      jsPsych.finishTrial(trial_data);
    });

  };

  return plugin;
})();
