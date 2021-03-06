var express = require("express");
var http    = require('http');
var path    = require('path');
var done    = false;
var app = express();
var methodOverride = require('method-override');
var fs = require('fs');
var busboy = require('connect-busboy');
var uuid = require('node-uuid');
var exec = require('child_process').exec;

app.use(busboy()); 
app.set('port', process.env.PORT || 3000);

// logging 
var morgan = require('morgan');
var accessLogStream = fs.createWriteStream(__dirname + '/access.log', {flags: 'a'})
app.use(morgan('combined', {stream: accessLogStream}))

// Routes
app.use(express.static(path.join(__dirname, 'public')));

app.get('/',function(req,res){
  res.sendFile(__dirname + "/index.html");
});

app.get('/about.html',function(req,res){
  res.sendFile(__dirname + "/about.html");
});


app.post('/', function(req, res) {
  var fstream;
  var uuidfn = uuid.v4(); 

  req.pipe(req.busboy);
  req.busboy.on('file', function (fieldname, file, filename) {
	  console.log("Uploading: " + filename + " to " + uuidfn); 
	  fstream = fs.createWriteStream(__dirname + '/uploads/' + uuidfn);
	  file.pipe(fstream);
	  fstream.on('close', function () {
	    res.writeHead(200);
	    res.end('{"ticket":"' + uuidfn + '"}');

	    var exec = require('child_process').exec;
	    /* build it */
	    exec("../sxsw_to_ical.py -nc -i uploads/" + uuidfn + " -o downloads/" + uuidfn + ".ics", function (error, stdout, stderr) {
   	      console.log(stdout);
	    });
	    
	  });
      });
});

app.use("/assets", express.static(__dirname + '/assets'));

app.use("/downloads", express.static(__dirname + '/downloads'));

// Start the app
http.createServer(app).listen(app.get('port'), function(){
  console.log("Express server listening on port " + app.get('port'));
});
