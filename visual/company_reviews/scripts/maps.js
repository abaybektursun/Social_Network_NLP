// Draw Default US map -----------------------------------------------------------------------------------------
function tooltipHtml(n, d){	/* function to create html content string in tooltip div. */
	return "<h4>"+n+"</h4><table>"+
		"<tr><td>Score</td><td>"+(d.score)+"</td></tr>"+
		"<tr><td>Sample Size</td><td>"+(d.ssize)+"</td></tr>"+
		"</table>";
}


var sampleData = {};	/* Sample random data. */
var reviews = [];

function ajax1() {
  return $.getJSON( "/us_map_data", function( json ) {
      reviews = json;
 });
};

// Wait until data is arrived
$.when(ajax1()).done(function(a1){
    // the code here will be executed when all four ajax requests resolve.
    // a1, a2, a3 and a4 are lists of length 3 containing the response text,
    // status, and jqXHR object for each of the four ajax calls respectively.
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
          
          if(reviews[i].state === d)
          {
              num_records += 1;
              score += reviews[i].overall_review_score;
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
	    sampleData[d]={
            score:parseFloat(score).toFixed(2),
            ssize:num_records,
            high:2, 
	        avg:1, color:color
        };
    }
);

/* draw states on id #statesvg */	
uStates.draw("#statesvg", sampleData, tooltipHtml);
d3.select(self.frameElement)
    .style("height", "600px")
    .classed("svg-container", true)
    .attr("preserveAspectRatio", "xMinYMin meet")
    .classed("svg-content-responsive", true); 
});

// Default checked ########################################
document.getElementById("checkbox-h-6b").checked = true;//#
//#########################################################
