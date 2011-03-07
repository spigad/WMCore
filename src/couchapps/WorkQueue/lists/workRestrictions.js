function(head, req) {

  // Apply restrictions provided in query to find elements that can run
  // at the given sites.

  // Include checks on data location, site white/blacklists & teams.

  // Return at least one element for each site with free job slots,
  // then take element size into account for further allocation.

    if (!req.query.resources) {
    	send(toJSON({}));
	    return;
    }
  
    try {
        var resources = JSON.parse(req.query.resources);
    } catch (ex) {
	    send('"Error parsing resources"');
	    return;
    }
  
    var teams = [];
    if (req.query.teams) {
	    try {
		    teams = JSON.parse(req.query.teams);
	    } catch (ex) {
	    	send('"Error parsing teams"');
		    return;
	    }
    }

    send("[");
    // loop over elements, applying site restrictions
    var first = true;
    while (row = getRow()) {
	    for (var site in resources) {
		    var ele = row["doc"]["WMCore.WorkQueue.DataStructs.WorkQueueElement.WorkQueueElement"];

		    // TODO: probably move this to a standalone function

	        // check work is for a team in the request
	        if (teams.length && ele["TeamName"] && teams.indexOf(ele["TeamName"]) === -1) {
	        	continue;
	        }

	        // skip if in blacklist
	        if (ele["SiteBlacklist"].indexOf(site) != -1) {
		        continue;
	        }
	        //skip if not in whitelist
	        if (ele["SiteWhitelist"].length != 0 && ele["SiteWhitelist"].indexOf(site) === -1) {
		        continue;
	        }

	        // input data restrictions
	        var hasData = true;
            for (var data in ele['Inputs']) {
    	        var locations = ele['Inputs'][data];
      	        if (locations.indexOf(site) === -1) {
      		        hasData = false; // data not at site, skip
      		        break;
      	        }
            }
	        if (hasData === false) {
		        continue; // skip to next site
	        }

	        // subtract element jobs from site resources
	        if (first !== true) {
		        send(",");
	        }
	        send(toJSON(row["doc"])); // need whole document, id etc...
	        var jobs = ele['Jobs'];
	        var slots = resources[site];
	        if (slots - jobs > 0) {
		        resources[site] = slots - jobs;
	        } else {
		        delete resources[site];
	        }

	        first = false; // from now on prepend "," to output
	        break; // we have work, move to next element (break out of site loop)

        } // end resources
    } // end rows

    send("]");
} // end function