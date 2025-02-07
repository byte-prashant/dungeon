
1) The parent package name should not contain hyphen("-"), it raise error while importing a packagge
2) Document.py change
    -- Ad folowing code to document .py code
        import debug
        debug.listen("localhost", 6528)
        debug.wait_for_client()
3) as OGA is dynamically importing packages in models.getclass() method,
   so in this case debugger is unalbe find the location, actua engine file
    to make it explicit import instead of __import__(), use imporlib
    
   add following code 

4) also create a launch.json in parent directory,inside .vscode folder
    > context 
        to run a game , OGA needs to have build of the engine
        so, now we have two engine classes, one inside build folder (1) and other original engine class (2)
        so while executing the game, interpreter uses file 1
        -- so make the engine file trackable to debuger and vscode [ so that breakpoints works]
        -- at point no 3 we will be importing file 1 [ the build engine file]
        in launch.json => remotefilepath == > location of the build engine
            localfilepath ==> location of original engine
    in this way  we will be able apply breakpoints to original file while debugger will be tracking the build engine file(1)

5) inside /do file,  increase the timeout of the  gunicorn