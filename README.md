# scap-security-guide-editor

The scap-security-guide-editor (ssge) is web-based editor for [The Extensible
Configuration Checklist Description Format (XCCDF)](https://scap.nist.gov/specifications/xccdf/)
and [The Open Vulnerability and Assessment Language (OVAL)](http://oval.mitre.org/)
formats. These formats belong to [The Security Content Automation Protocol (SCAP)](https://scap.nist.gov/)
protocol family. The main purpose of this editor is to foster content creation
in [the scap-security-guide](https://www.open-scap.org/security-policies/scap-security-guide/)
SCAP community content project.

##Using the editor

Start the editor by the ssge command if you installed the rpm or running ssge/ssge.py
if downloaded the code. When started for the first time, the ssge will clone
scap-security-guide git repository to ~/.scap-security-guide-git. This repository
clone should be used by the ssge tool only. If you need local clone of scap-security-guide
git repository for any other purposes, clone it somewhere else since your changes would be
discarded by the editor. When git clone is completed, you should see output like
 * Running on http://0.0.0.0:4444/
The ssge is now running on your computer. To start working with the ssge, open
http://localhost:4444/ address in your web browser.

####Mode selector
![mode selector](https://github.com/pbenas/scap-security-guide-editor/blob/master/docs/modeselector.png)

The mode selector page is the start screen of the ssge. The first part is dedicated to
scap-security-guide XCCDF files. You can select XCCDF file from the git repository and
open in in the editor. If you select a file and hit the Delete button, you'll receive
a patch deleting selected file. You can also create new XCCDF file in one of existing
directories. After pressing the Create new button, the new file dialogue is displayed.
On the new file screen, you have to select name for the new file and choose directory,
in which the new file will be created. Then editor with the new file template is displayed.

The second section of the mode selector screen works the same way the first does,
but it's used for scap-security-guide OVAL files. In the last section, you can simply
upload any XCCDF or OVAL file from your computer and edit it in the editor.

###Editor
![editor](https://github.com/pbenas/scap-security-guide-editor/blob/master/docs/ssgxccdf.png)

The editor page is the main screen of the scap-security-guide-editor. The main part
is the textarea containing the file being edited. There are several options accessible
in form of buttons located at the bottom of the editor screen. The options available are
dependent on currently edited content, the above example screenshot was taken when editing
an XCCDF file from scap-security-guide git. The leftmost button is used for obtaining
result of editing. When editing file from git, it gives a patch against git HEAD. Such
patch can be sent to scap-security-guide mailing list for review and inclusion or directly
applied and committed. When editing uploaded custom file, this button gives the whole
modified file.

The Validate button will perform openscap validation of the currently edited content.
If user custom file is being edited, it's validated directly. If an XCCDF or OVAL file
from git is being edited, the result file is being built first and then validated.
It's not possible to validate just the piece of content currently being edited since
it does not comply with the standards. This is the reason, why you sometimes can see
make failures on validation attempt.

Note for Fedora 18 and newer users: Content validation currently does not work with
libxslt-1.1.27 and newer due to
[this](http://www.mail-archive.com/scap-security-guide@lists.fedorahosted.org/msg02140.html).
Downgrading libxslt to 1.1.26 is a workaround
until this problem is fixed by scap-security-guide developers.

The Close button just brings you back to mode selector screen. When editing an XCCDF
file, there are 'Add Rule' and 'Add Group' buttons available. These buttons helps with
adding corresponding tags by generating minimal Rule/Group template at the cursor
position upon pressing.

The scap-security-guide-editor has feature of autocompletion for XCCDF as well as OVAL
formats. This feature is accessible for child elements, element attributes and OVAL id
references within scap-security-guide project. After pressing '<', ' ' (spacebar)
and '=' (only for id attribute of the oval tag) keys, a suggestion pop-up menu is
displayed, when available. For the possible suggestions, short help is displayed on
mouse hover, as shown on above example.

###Bugs and feature requests

If you find a bug in the editor or would like to see some functionality in it,
feel free to open new ticket. If the ssge behaves inconsistently with SCAP
format specifications, the specifications are right.

If you're getting HTTP 500 responses from the application, try running it with
'--debug' parameter. You'll get python traceback which can be very helpful in
finding out what has gone wrong.
