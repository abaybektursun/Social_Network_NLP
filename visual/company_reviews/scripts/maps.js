// Draw Default US map -----------------------------------------------------------------------------------------
function tooltipHtml(n, d){	/* function to create html content string in tooltip div. */
	return "<h4>"+n+"</h4><table>"+
		"<tr><td>Score</td><td>"+(d.score)+"</td></tr>"+
		"<tr><td>Sample Size</td><td>"+(d.ssize)+"</td></tr>"+
		"</table>";
}


var sData = {};
var reviews = [];
var reviews_swp = [];
var score_field = "overall_review_score";
var min_date = max_date = moment();
var low_date = high_date = moment();
var duration = moment.duration(max_date.diff(min_date));

function ajax1() {
  return $.getJSON( "/us_map_data", function( json ) {
      reviews = json;
 });
};

function render_us_map(){
        ["HI", "AK", "FL", "SC", "GA", "AL", "NC", "TN", "RI", "CT", "MA",
         "ME", "NH", "VT", "NY", "NJ", "PA", "DE", "MD", "WV", "KY", "OH",
         "MI", "WY", "MT", "ID", "WA", "DC", "TX", "CA", "AZ", "NV", "UT",
         "CO", "NM", "OR", "ND", "SD", "NE", "IA", "MS", "IN", "IL", "MN",
         "WI", "MO", "AR", "OK", "KS", "LS", "VA"]
            .forEach(
            function(d){
                var score=0,
                    num_records=0,
                    mid=1,
                    high=2;
                for(var i = 0; i < reviews.length; i++)
                {
                    if(
											reviews[i].state === d &&
											moment(reviews[i].post_date) <= high_date &&
											moment(reviews[i].post_date) >= low_date
										)
                    {
                        num_records += 1;
                        score += reviews[i][score_field];
                    }
                }
                score /= num_records;
                var color;
                if (num_records == 0){
                    color = "#ffffff";
                }
                else{
                    color = d3.interpolate("#800026","#ffffcc")(score/5);
                }
                sData[d]={
                    score:parseFloat(score).toFixed(2),
                    ssize:num_records,
                    high:2,
                    avg:1, color:color
                };
            }
        );

        uStates.draw("#statesvg", sData, tooltipHtml);
        d3.select(self.frameElement)
            .style("height", "600px")
            .classed("svg-container", true)
            .attr("preserveAspectRatio", "xMinYMin meet")
            .classed("svg-content-responsive", true);

}

// After getting data max and min dates are calculated
function max_min_date() {

	  var momentDate;
		var momentMax, momentMin;

    momentDate = moment(reviews[0].post_date);
		momentMax = momentDate; momentMin = momentDate;
    for(var i = 1; i < reviews.length; i++)
		{
			momentDate = moment(reviews[i].post_date);
			if(momentDate > momentMax) {momentMax = momentDate}
			if(momentDate < momentMin) {momentMin = momentDate}
		}

		min_date = low_date = momentMin;
		max_date = high_date = momentMax;

		duration = moment.duration(max_date.diff(min_date));
}


// Wait until data is arrived
$.when(ajax1()).done(function(a1){
// the code here will be executed when all four ajax requests resolve.
// a1, a2, a3... are lists of length 3 containing the response text,
// status, and jqXHR object for each of the four ajax calls respectively.
    max_min_date();
    render_us_map();
});

// perc - percent
function perc_to_date(perc) {
		var days = duration.asDays();
		var adjust_days = Math.floor(days * perc);
		var perc_date = min_date.clone();
		perc_date.add(adjust_days, 'days');
		return perc_date;
}

// Default checked ########################################
//document.getElementById("comps").value = "HPE";       //#
//#########################################################

$("#comps_submit")
    .button()
    .click(function(){
        var cmp = document.getElementById('comps').value;
        function get_reviews() {
            return $.getJSON( "/us_map_data", {company: cmp},
                function( json ) {
                    reviews = json;
                }
            );
        };
        $.when(get_reviews()).done(function(a1){
					  max_min_date();
            render_us_map();
        })
    });

// Filters --------------------------------------------------------------------------------------------------
var nonLinearSlider = document.getElementById('datef');

noUiSlider.create(nonLinearSlider, {
	connect: true,
	behaviour: 'tap-drag',
	start: [ 0, 1 ],
	range: {
		'min': [ 0 ],
		'max': [ 1 ]
	}
});

var node = document.getElementById('inter-values')
// Display the slider value and how far the handle moved
// from the left edge of the slider.
var sliders = [0.0, 0.0];
nonLinearSlider.noUiSlider.on('update',
	function ( values, handle, unencoded, isTap, positions ) {
		sliders[handle] = values[handle];
		node.innerHTML = 'From ' + perc_to_date(sliders[0]).format('ll') + ' to ' + perc_to_date(sliders[1]).format('ll');
	}
);

nonLinearSlider.noUiSlider.on('end',
	function ( values, handle, unencoded, isTap, positions ) {
		sliders[handle] = values[handle];
		low_date  = perc_to_date(sliders[0]);
		high_date = perc_to_date(sliders[1]);
		render_us_map();
	}
);

$(document).ready(function() {
    $('input:radio[name=radios]').change(function() {
         score_field = this.id;
				 render_us_map();
    });
});
