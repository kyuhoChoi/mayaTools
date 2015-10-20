# -*- coding:utf-8  -*-
u'''import render.backburnerTools as bb

# 다른씬의 1,2,3,50,20,40 프레임만 따로 렌더 : 해당 파일을 열지 않아도 됨
bb.submitJob( 
	manager = 'alfredtools',          # 백버너 매니저 일름
	jobName = 'DR_G_05_camD_re',      # 잡이름.
    # description = 'Kyuhos Work File', # 잡 설명 ( 필요 없으면 무시해도 됨.)	
	priority = 30,                    # 우선순위
    taskSize = 1,                     # 한번에 몇장 
    
    sceneFile = 'X:/2014_Nexon_Durango/3D_project/Share/scenes/Render/G_05_camD.mb', # 씬파일명, (현재열린씬을 걸려고 하면 무시해도 됨.)
    # startFrame   = 0,               # 파일 렌더세팅 기준으로 하려면 명시하지 말것.
    # endFrame     = 100,             # 파일 렌더세팅 기준으로 하려면 명시하지 말것.
	# frames = [367]                  # 렌더 프레임이 연속적이지 않을때 사용.
	)

# 현재씬 렌더
bb.submitJob()

# 현재씬 렌더 2 : 한프레임만 다시 렌더
bb.submitJob( 
    manager = '%(manager)s',
    jobName = '%(jobName)s',     
    frames  = [67]
    )

# 현재씬 렌더 3
bb.submitJob( jobName='%(jobName)s', taskSize=5 )

# 현재씬의 1,2,3,50,20,40 프레임만 따로 렌더
bb.submitJob( frames=[1,2,3,50,20,40], jobName='%(jobName)s', priority=1 )

# 축약 버전 1
bb.submitJob(
    sceneFile    = '%(sceneFile)s',
    startFrame   = %(startFrame)s,
    endFrame     = %(endFrame)s,
    taskSize     = 1,
    jobName      = '%(jobName)s',
    )

# 옵션 전체
bb.submitJob(
    projectSet   = '%(projectSet)s',
    destPath     = '%(destPath)s',
    sceneFile    = '%(sceneFile)s',
    startFrame   = %(startFrame)s,
    endFrame     = %(endFrame)s,
    taskSize     = 1,
    jobName      = '%(jobName)s',
    description  = 'Kyuhos Work File', 
    priority     = 50,
    manager      = '%(manager)s'
    cmdjob       = '%(cmdjob)s',
    rendererPath = '%(rendererPath)s',
    taskList     = '%(taskList)s'
    )

'''
import maya.cmds as cmds
import maya.mel as mel
import os, sys
 
def submitJob( **kwargs ):
    bbCmd = makeBackburnerCmd(**kwargs)
    os.system( bbCmd )
    print 'os.system( \'%s\' )' % bbCmd

def makeBackburnerCmd( **kwargs ):
    u'''
    makeBackburnerCmd(
        sceneFile    = 'Z:/3D_project/Share/scenes/render/E_02_camA.mb',
        startFrame   = 0,
        endFrame     = 100,
        taskSize     = 1,
        jobName      = 'E_02_camA',
        rendererPath = 'C:/Program Files/Autodesk/Maya2012/bin/Render',
        )

    makeBackburnerCmd(
        projectSet   = 'Z:/3D_project/Share',
        destPath     = 'Z:/3D_project/Share/images',
        sceneFile    = 'Z:/3D_project/Share/scenes/render/E_02_camA.mb',
        startFrame   = 0,
        endFrame     = 100,
        taskSize     = 1,
        jobName      = 'E_02_camA',
        description  = 'Kyuhos Work File', 
        priority     = 50,
        manager      = 'alfredprinter',
        cmdjob       = 'C:/Program Files (x86)/Autodesk/Backburner/cmdjob.exe',
        rendererPath = 'C:/Program Files/Autodesk/Maya2012/bin/Render',
        taskList     = 'C:/Users/ADMINI~1/AppData/Local/Temp/E_01_camA.txt'
        )
    '''

    sceneFile    = kwargs.get('sceneFile',    cmds.file(q=True, sceneName=True) ).replace('\\','/')
    startFrame   = kwargs.get('startFrame',   cmds.getAttr('defaultRenderGlobals.startFrame') )
    endFrame     = kwargs.get('endFrame',     cmds.getAttr('defaultRenderGlobals.endFrame') )
    frames       = kwargs.get('frames')
    taskSize     = kwargs.get('taskSize',     1 )
    jobName      = kwargs.get('jobName',      mel.eval('basenameEx("%s")'%sceneFile) )
    description  = kwargs.get('description',  '' )
    priority     = kwargs.get('priority',     50 )
    manager      = kwargs.get('manager',      'alfredtools' )
    projectSet   = kwargs.get('projectSet',   getCurrentProjectSet() ).replace('\\','/')
    destPath     = kwargs.get('destPath',     getImagePath() ).replace('\\','/')
    cmdjob       = kwargs.get('cmdjob',       getBackburnerPath() ).replace('\\','/')
    rendererPath = kwargs.get('rendererPath', getMayaRendererPath() ).replace('\\','/')
    taskList     = kwargs.get('taskList',     getMayaTempPath()+'/%s.txt' % jobName ).replace('\\','/')

    taskList
    
    r = 'file',
    s = '%tp2',
    e = '%tp3',

    # taskList 파일 생성
    taskListString = makeTaskList( startFrame, endFrame, frames, taskSize)
    taskList = writeFile( taskList, taskListString )

    bbCmd  = ''
    bbCmd += '""%(cmdjob)s" '                   # 앞에 쌍따옴표로 시작해야함.. 이해하긴 어렵지만.. 역슬래시 때문인듯 함.
    bbCmd += '-jobName "%(jobName)s" '
    bbCmd += '-description "%(description)s" '
    bbCmd += '-manager %(manager)s '
    bbCmd += '-priority %(priority)d '
    bbCmd += '-taskList "%(taskList)s" '
    bbCmd += '-taskName 1 '

    bbCmd += '"%(rendererPath)s" '
    bbCmd += '-r file -s %%tp2 -e %%tp3 '
    bbCmd += '-proj "%(projectSet)s" '
    bbCmd += '-rd "%(destPath)s"  '

    bbCmd += '"%(sceneFile)s"'

    return bbCmd % locals()

def makeTaskList( startFrame=0, endFrame=300, frames=[], taskSize=1 ):
    txt = ''
    
    if frames:
        print frames
        for frame in frames:
            txt += 'frames%d-%d\t%d\t%d\n' % (frame,frame,frame,frame)
    
    else: 
        for i in range( int(startFrame), int(endFrame+1), int(taskSize) ):
            s = i
            e = i+(taskSize-1)
            if e > endFrame : 
                e = endFrame
            txt += 'frames%d-%d\t%d\t%d\n' % (s,e,s,e)

    return txt

def writeFile( filePath='D:/Users/Desktop/myaypython.txt', txt='hello' ):
    f=open( filePath, 'w+')
    f.write(txt)
    f.close()

    return filePath

def getBackburnerPath():
    return 'C:/Program Files (x86)/Autodesk/Backburner/cmdjob.exe'

def getImagePath():
    return getCurrentProjectSet()+'/images'

def getCurrentProjectSet():
    return cmds.workspace(q=1,rd=1)[:-1]

def getMayaRendererPath():
    return os.path.join( os.path.split( sys.executable )[0], 'Render' )

def getMayaTempPath():
    return os.environ.get('TEMP').decode('cp949')

def ui():
    def scriptWindow( document ):
        win = cmds.window( title='Code Reference - Python Script Editor ', wh=(700,300))
        cmds.frameLayout(labelVisible=False, borderVisible=False)
        # -----------------------------------------------
        
        cmds.cmdScrollFieldExecuter( sourceType="python", text=document )
        
        # -----------------------------------------------            
        cmds.showWindow(win)
    
    sceneFile    = cmds.file(q=True, sceneName=True).replace('\\','/')
    startFrame   = cmds.getAttr('defaultRenderGlobals.startFrame')
    endFrame     = cmds.getAttr('defaultRenderGlobals.endFrame')
    frames       = [10,11,12,15]
    taskSize     = 1
    jobName      = mel.eval('basenameEx("%s")'%sceneFile)
    description  = ''
    priority     = 50
    manager      = 'alfredtools'
    projectSet   = getCurrentProjectSet().replace('\\','/')
    destPath     = getImagePath().replace('\\','/')
    cmdjob       = getBackburnerPath().replace('\\','/')
    rendererPath = getMayaRendererPath().replace('\\','/')
    tmpFile      = getMayaTempPath() +'/' + jobName + '.txt'
    taskList     = tmpFile.replace('\\','/')
   
    scriptWindow( __doc__ % locals()  )
 
    
'''
#
#    References
#
#
#


CMDJOB <options> executable_to_run <executable parameters>

Submits a command line job to Backburner.


                            -OPTIONS-

   -?                            - Show this help file.
   -cmdFile:<files>              - Semi-colon seperated list of text files
     OR                            that contains any of the options below.
   @<files>                        Can be used alongside these options.

                           -JOB OPTIONS-

   -jobName:<name>               - Job name. Default is 'cmdJob'.
   -jobNameAdjust                - Add a number to the name if it already  exists in the queue.
   -description:<string>         - Sets a description for the job.
   -priority:<number>            - Sets job's priority. Default is 50.
   -workPath:<folder>            - Working folder for cmdjob.exe and servers. Used to resolve relative paths for running the executable. Default for cmdjob.exe is the current path. Default for the Servers is Backburner's.
   -logPath:<folder>             - Task log folder. Default is to not produce a log.
   -showOutput:<files>           - Semi colon seperated list of output files to be accessible from the Monitor.

                          -SUBMIT OPTIONS-

   -dependencies:<job names>     - Semi-colon list of job dependencies.
   -timeout:<minutes>            - Sets a timeout per task. Default is 60 minutes.
   -attach                       - Attaches the executable to the job.
   -progress                     - Monitor the job progress.
   -suspended                    - Starts the job suspended.
   -leaveInQueue                 - Keep job in queue after completion. Default is to use manager settings.
   -archive                      - Archive job on completion.
     OR
   -archive:<days>               - Archive job after specified number of days(1 or more) after job completion. Default is to use manager settings.(Ignored when -leaveInQueue is used)
   -delete                       - Delete job on completion.
     OR
   -delete:<days>                - Delete job after specified number of days (1 or more) after job completion. Default is to use manager settings. (Ignored when -leaveInQueue is used) (Ignored when -archive is used)
   -nonconcurrent                - Tasks are executed in a sequence.
   -dontBlockTasks               - Disables task blocking for this job. Default is to use global settings.
   -blockTasks                   - Forces task blocking for this job. Default is to use global settings.
   -perServer                    - Creates seperate jobs that are identical to this job, and assigns one to each server assigned to this job.  Each server will perform the same tasks as the others.

                          -NETWORK OPTIONS-

   -manager:<name>               - Manager name, default is automatic search.
   -netmask:<mask>               - Network mask.
   -port:<number>                - Port number.
   -servers:<servers>            - Semi colon seperated list of servers.(Ignored if a group is used)
   -serverCount:<number>         - Max number of servers that can work on this job at any point in time.
   -group:<group>                - Group name of servers to use.

                            -PARAMETERS-

   -taskList:<file>              - File contains a tab seperated table. Use fill-in tokens to reference the table.
   -taskName:<index>             - Sets the task name from the task list file 0=Unnamed, 1-X=column index in the file
   -numTasks:<number>            - Number of tasks to perform.(Ignored if -taskList is used)
   -tp_start:<number>            - Specify the starting value of an internally generated table used as a task list file. (Ignored if -taskList is used)
   -tp_jump:<number>             - Specify the increment of the internally generated table used as a task list file.(Ignored if -taskList is used)
   -jobParamFile:<file>          - File with two tab-seperated column used to add custom data to the job. The first colum is the parameter's name. The second column is the parameter's value.

                        -NOTIFICATION OPTIONS-

   -emailFrom:<address>          - Source email address for notification.
   -emailTo:<address>            - Destination email address for notification.
   -emailServer:<server>         - SMTP name of email server to use.
   -emailCompletion              - Notify by email job completion.
   -emailFailure                 - Notify by email job failure.
   -emailProgress:<number>       - Notify by email the completion of every
                                   Nth task

                           -FILL-IN TOKENS-

   Placeholder tokens that are replaced while calling executable.
   These are evaluated on a per server basis.
   These are not recursive.  For example, %tp1 cannot evaluate to
   contain a fill-in token itself.

   %jn                           - Job name.
   %dsc                          - The job description.
   %srv                          - Name of the server executing the task.
   %tpX                          - Task parameter X from the task list. X, column index in the task list file. Rows correspond to the current task #.
   %*tpX                         - Same as %tpX *, number of 0 padded digits to use.
   %tn                           - Task number of the assigned task.
   %*tn                          - Same as %tn *, number of 0 padded digits to use.
   %jpX                          - Parameter X from the job parameter file. X, row index in the job parameter file.
   %*jpX                         - Same as %jpX *, number of 0 padded digits to use.

                               -NOTES-

   Options are not case-sensitive.
   Only the FIRST occurrence of cmdFile/@ is used, the others are ignored.
   Only the LAST occurrence of each other option is used.








system("Render.exe -r file -help");
# Result:
Usage: Render.exe [options] filename
       where "filename" is a Maya ASCII or a Maya binary file.

Common options:
  -help              Print help
  -test              Print Mel commands but do not execute them
  -verb              Print Mel commands before they are executed
  -keepMel           Keep the temporary Mel file
  -listRenderers     List all available renderers
  -renderer string   Use this specific renderer
  -r string          Same as -renderer
  -proj string       Use this Maya project to load the file
  -log string        Save output into the given file

Specific options for renderer "file": Use the renderer stored in the Maya file

General purpose flags:
  -rd path                       Directory in which to store image file
  -of string                     Output image file format. See the Render Settings window to
        find available formats
  -im filename                   Image file output name

Frame numbering options
  -s float                       Starting frame for an animation sequence
  -e float                       End frame for an animation sequence
  -b float                       By frame (or step) for an animation sequence
  -pad int                       Number of digits in the output image frame file name
        extension
  -rfs int                       Renumber Frame Start: number for the first image when
        renumbering frames
  -rfb int                       Renumber Frame By (or step) used for renumbering frames
  -fnc int                       File Name Convention: any of name, name.ext, ... See the
        Render Settings window to find available options. Use namec and
        namec.ext for Multi Frame Concatenated formats. As a shortcut,
        numbers 1, 2, ... can also be used

Camera options
  -cam name                      Specify which camera to be rendered
  -rgb boolean                   Turn RGB output on or off
  -alpha boolean                 Turn Alpha output on or off
  -depth boolean                 Turn Depth output on or off
  -iip                           Ignore Image Planes. Turn off all image planes before
        rendering

Resolution options
  -x int                         Set X resolution of the final image
  -y int                         Set Y resolution of the final image
  -percentRes float              Renders the image using percent of the resolution
  -ard float                     Device aspect ratio for the rendered image
  -par float                     Pixel aspect ratio for the rendered image

Render Layers and Passes:
  -rl boolean|name(s)            Render each render layer separately
  -rp boolean|name(s)            Render passes separately. 'all' will render all passes
  -sel boolean|name(s)           Selects which objects, groups and/or sets to render
  -l boolean|name(s)             Selects which display and render layers to render

Mel callbacks
  -preRender string              Mel code executed before rendering
  -postRender string             Mel code executed after rendering
  -preLayer string               Mel code executed before each render layer
  -postLayer string              Mel code executed after each render layer
  -preFrame string               Mel code executed before each frame
  -postFrame string              Mel code executed after each frame
  -pre string                    Obsolete flag
  -post string                   Obsolete flag

Specific options for the layers who use Maya software renderer:

Anti-aliasing quality only for Maya software renderer:
  -sw:eaa int                    The anti-aliasing quality of EAS (Abuffer). One of: highest(0), high(1), medium(2), low(3)
  -sw:ss int                     Global number of shading samples per surface in a pixel
  -sw:mss int                    Maximum number of adaptive shading samples per surface in a pixel
  -sw:mvs int                    Number of motion blur visibility samples
  -sw:mvm int                    Maximum number of motion blur visibility samples
  -sw:pss int                    Number of particle visibility samples
  -sw:vs int                     Global number of volume shading samples
  -sw:ufil boolean               If true, use the multi-pixel filtering; otherwise use single pixel filtering
  -sw:pft int                    When useFilter is true, identifies one of the following filters: box(0), triangle(2), gaussian(4), quadratic(5)
  -sw:pfx float                  When useFilter is true, defines the X size of the filter
  -sw:pfy float                  When useFilter is true, defines the Y size of the filter
  -sw:rct float                  Red channel contrast threshold
  -sw:gct float                  Green channel contrast threshold
  -sw:bct float                  Blue channel contrast threshold
  -sw:cct float                  Pixel coverage contrast threshold (default is 1.0/8.0)

Raytracing quality only for Maya software renderer:
  -sw:ert boolean                Enable ray tracing
  -sw:rfl int                    Maximum ray-tracing reflection level
  -sw:rfr int                    Maximum ray-tracing refraction level
  -sw:sl int                     Maximum ray-tracing shadow ray depth

Field Options only for Maya software renderer:
  -sw:field boolean              Enable field rendering. When on, images are interlaced
  -sw:pal                        When field rendering is enabled, render even field first (PAL)
  -sw:ntsc                       When field rendering is enabled, render odd field first (NTSC)

Motion Blur only for Maya software renderer:
  -sw:mb boolean                 Motion blur on/off
  -sw:mbf float                  Motion blur by frame
  -sw:sa float                   Shutter angle for motion blur (1-360)
  -sw:mb2d boolean               Motion blur 2D on/off
  -sw:bll float                  2D motion blur blur length
  -sw:bls float                  2D motion blur blur sharpness
  -sw:smv int                    2D motion blur smooth value
  -sw:smc boolean                2D motion blur smooth color on/off
  -sw:kmv boolean                Keep motion vector for 2D motion blur on/off

Render Options only for Maya software renderer:
  -sw:ifg boolean                Use the film gate for rendering if false
  -sw:edm boolean                Enable depth map usage
  -sw:g float                    Gamma value
  -sw:premul boolean             Premultiply color by the alpha value
  -sw:premulthr float            When premultiply is on, defines the threshold used to determine whether to premultiply or not

Memory and Performance only for Maya software renderer:
  -sw:uf boolean                 Use the tessellation file cache
  -sw:oi boolean                 Dynamically detects similarly tessellated surfaces
  -sw:rut boolean                Reuse render geometry to generate depth maps
  -sw:udb boolean                Use the displacement bounding box scale to optimize displacement-map performance
  -sw:mm int                     Renderer maximum memory use (in Megabytes)

Specific options for the layers who use Maya hardware renderer:

Quality flags only for Maya hardware renderer:
  -hw:ehl boolean                Enable high quality lighting
  -hw:ams boolean                Accelerated multi sampling
  -hw:ns int                     Number of samples per pixel
  -hw:tsc boolean                Transparent shadow maps
  -hw:ctr int                    Color texture resolution
  -hw:btr int                    Bump texture resolution
  -hw:tc boolean                 Enable texture compression

Render options only for Maya hardware renderer:
  -hw:c boolean                  Culling mode. 0: per object. 1: all double sided. 2: all single sided
  -hw:sco boolean                Enable small object culling
  -hw:ct float                   Small object culling threshold

Mel callbacks only for Maya hardware renderer:
  -hw:mb boolean                 Enable motion blur
  -hw:mbf float                  Motion blur by frame
  -hw:ne int                     Number of exposures
  -hw:egm boolean                Enable geometry mask

Specific options for the layers who use Mentalray renderer

Other only for Mentalray renderer:
  -mr:v/mr:verbose int           Set the verbosity level. 0 to turn off messages 1 for fatal errors only 2 for all errors 3 for warnings 4 for informational messages 5 for progress messages 6 for detailed debugging messages
  -mr:rt/mr:renderThreads int    Specify the number of rendering threads.
  -mr:art/mr:autoRenderThreads   Automatically determine the number of rendering threads.
  -mr:mem/mr:memory int          Set the memory limit (in MB).
  -mr:aml/mr:autoMemoryLimit     Compute the memory limit automatically.
  -mr:ts/mr:taskSize int         Set the pixel width/height of the render tiles.
  -mr:at/mr:autoTiling           Automatically determine optimal tile size.
  -mr:fbm/mr:frameBufferMode int Set the frame buffer mode. 0 in-memory framebuffers 1 memory mapped framebuffers 2 cached framebuffers
  -mr:rnm boolean                Network rendering option. If true, mental ray renders almost everything on slave machines, thus reducing the workload on the master machine
  -mr:lic string                 Specify satellite licensing option. mu/unlimited or mc/complete.
  -mr:reg int int int int        Set sub-region pixel boundary of the final image: left, right, bottom, top
 *** Remember to place a space between option flags and their arguments. ***
Any boolean flag will take the following values as TRUE: on, yes, true, or 1.
Any boolean flag will take the following values as FALSE: off, no, false, or 0.

    e.g. -s 1 -e 10 -x 512 -y 512 -cam persp -mr:v 5 file.

 #

'''