function ProTo2() {
    this.try = 0;
    this.started = false;
    this.starting = false;
    this.wait = false;
    this.entry = null;
}

ProTo2.prototype.forward = function() {
	if (location.search.indexOf('proto_tool_id=') != -1 || location.search.indexOf('tool_id=proto_') != -1) {
		var self = this;
		//self.log('checking for ProTo2');
		$.getJSON('/api/entry_points?running=true')
        .done( function (data) {
            for (var entry of data) {
                if (entry.active && entry.name.startsWith('ProTo')) {
                    if (!self.entry) {
                        self.entry = entry;
                        self.log(entry.target);
                    }
                    if (!self.starting) {
                        try {
                            galaxy_main.location.replace(entry.target + location.search);
                            self.try = 100;
                        } catch (e) {
                            self.log(e)
                            //self.wait = true;
                            //self.try = 1;
                            //self.started = true;
                        }
                    } else if (self.started) {
                        self.wait = true;
                        $.get(entry.target + location.search)
                            .done(function () {
                                self.try = 100;
                                galaxy_main.location.replace(entry.target + location.search);
                            })
                            .fail(function () {
                                //self.wait = false;
                                self.retry(); //setTimeout(function(){ self.forward() }, 250);
                            });
                    }
                }
            }
            if (self.try == 0 && !self.entry) {
                self.log('Starting ProTo2 UI interactive tool...');
                self.start();
            }
            if (!self.wait) self.retry();
        })
        .fail( function () {
                self.log('api call failed');
        });
	}
}

ProTo2.prototype.retry = function () {
    var self = this;
    self.try ++;
    if (self.try < 100) {
        self.log('.', false);
        setTimeout(function(){ self.forward(); }, 300);
    }
}

ProTo2.prototype.log = function (msg, br=true) {
    console.log(msg);
    try {
        galaxy_main.document.writeln(msg + (br ? "<br>" : ""));
    } catch (e) {
        console.log(e);
    }
}

ProTo2.prototype.start = function () {
    var self = this;
    self.starting = true;
    $.post('/api/tools', {tool_id: 'interactive_tool_proto2'},
        function (data) {
            console.log(data);
            self.job_id = data.jobs[0]['id'];
            self.started = true;
        }
    );
}

$(window).on('load', function() {
    var proto = new ProTo2();
    proto.forward();
});
