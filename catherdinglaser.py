#!/usr/bin/env python

# Cat Herding Laser

import cherrypy # Download at: http://cherrypy.org/
import hashlib # For Survey ID generation
import random

class Letter_Block(object):

    """ class Letter_Block: Parent Class for all other Block objects; not called directly.
    """
    
    def __init__(self):
        self.required_field = False

    def Get_DDC(self):
        return []

    def GetTitle(self):
        return []

    def SetRequired(self, whether_required):
        assert (whether_required == True or whether_required == False), "whether_required must be boolean."
        self.required_field = whether_required

    def Get_Permutations(self):
        return 1

class Static_Block(Letter_Block):

    """ class Static_Block(Letter_Block): used for any independent static string.  Common usage: static headers and footers, static in-between text.
    """
    
    def __init__(self, are_written_as):
        super(Static_Block, self).__init__()
        self.block_type = "Static_Block"
        self.alias = "Text"
        self.are_written_as = are_written_as

    def Get_AWA(self):
        return [self.are_written_as]

    def SetValue(self, are_written_as):
        self.are_written_as = are_written_as

class Randomized_Static_Block(Letter_Block):

    """ class Randomized_Static_Block(Letter_Block): used for a randomized independent static string. Common usage: static headers and footers, static in-between text.
        Example: a = Randomized_Static_Block(["any", "one", "of", "these", "will", "be", "picked"])
    """

    def __init__(self, *args):
        super(Randomized_Static_Block, self).__init__()
        self.block_type = "Randomized_Static_Block"
        self.alias = "Random Text"
        self.are_written_as = args[0]

    def Get_AWA(self):
        return [random.choice(self.are_written_as)]

    def SetValues(self, are_written_as):
        if type(are_written_as) == list: # I hate to do explicit type testing but Randomized_Static_Blocks don't work without a list to choose from
            self.are_written_as = are_written_as

    def Get_Permutations(self):
        return len(self.are_written_as)

class Dynamic_Block(Letter_Block):

    """ class Dynamic_Block(Letter_Block): used for dependent dynamic strings.  Common usage: a radio button or checkbox(es) with different label text than output text.
        Example: a = Dynamic_Block("Numbers corresponding to letters",[1,2,3],["a","b","c"])
    """
    
    def __init__(self, *args):
        super(Dynamic_Block, self).__init__()
        self.block_type = "Dynamic_Block"
        self.alias = "Radio"

        self.display_title = args[0]
        self.display_during_choice = args[1]
        self.are_written_as = args[2]
        self.Enforce_Length()

    def Get_DDC(self, items = None): 

        """\t Get_DDC(items): Returns the 'Display During Choice' values for the specified list items.
        """

        if items is None:
            items = xrange(len(self.display_during_choice))
        
        self.DDCs = []
        for x in items:
            self.DDCs.append(self.display_during_choice[x])
        return self.DDCs         

    def Get_AWA(self, items = None):

        """\t Get_AWA(items): Returns the 'Are Written As' values for the specified list items.
        """

        if items is None:
            items = xrange(len(self.are_written_as))

        self.AWAs = []
        for x in items:
            self.AWAs.append(self.are_written_as[x])
        return self.AWAs

    def GetTitle(self):
        return self.display_title

    def SetTitle(self, display_title):
        self.display_title = display_title

    def GetValues(self):
        return (self.display_during_choice, self.are_written_as)

    def SetValues(self, *args):

        """\t SetValues(*args): Sets the 'Display During Choice' and 'Are Written As' values and checks that both lists are the same length.
        """

        self.display_during_choice = args[0]
        self.are_written_as = args[1]
        self.Enforce_Length()

    def Enforce_Length(self):
        assert (len(self.display_during_choice) == (len(self.are_written_as))), "Display During Choice and Are Written As need to contain the same number of items in their lists."

    def Get_Permutations(self):
        if self.required_field == True:
            return len(self.are_written_as)
        else:
            return len(self.are_written_as)+1

class Randomized_Dynamic_Block(Dynamic_Block):

    """ class Randomized_Dynamic_Block(Dynamic_Block): used for randomized dependent dynamic strings.  Identical to Dynamic_Block except output text is randomized from a given list.
        Example: a = Randomized_Dynamic_Block("Display title",[1,2,3],[({1: [33,22,11]}),({2: [44,55,66]}),({3: [55,66,77]})])
    """
    
    def __init__(self, *args):
        super(Randomized_Dynamic_Block, self).__init__(*args)
        self.block_type = "Randomized_Dynamic_Block"
        self.alias = "Random Radio"
        
    def Get_AWA(self, items = None):

        """\t Get_AWA(item): Returns the 'Are Written As' value for the specified list item, randomly selected from the corresponding list.
        """

        if items is None:
            items = xrange(len(self.are_written_as))

        self.possible_values = []

        for x in items:
            self.possible_values.extend(self.are_written_as[x].values())
            
        return random.choice(random.choice(self.possible_values))

    def Get_Permutations(self):

        if self.required_field == True:
            one_if_optional = 0
        else:
            one_if_optional = 1

        permutations = 0
        
        for x in xrange(len(self.are_written_as)): 
            permutations += len(self.are_written_as[x].values().pop()) 

        return permutations + one_if_optional
            

class Multiple_Dynamic_Block(Dynamic_Block):

    """ class Multiple_Dynamic_Block(Dynamic_Block): used for returning multiple dependent dynamic strings while preserving natural language. Otherwise identical to Dynamic_Block.
        Example: a = Multiple_Dynamic_Block("Display title",[1,2],[("a", " this goes in between "), ("b", "this also goes in between")])
    """
    
    def __init__(self, *args):
        super(Multiple_Dynamic_Block, self).__init__(*args)
        self.block_type = "Multiple_Dynamic_Block"
        self.alias = "Checkbox"

    def Get_AWA(self, items = None):

        """ Get_AWA(items): Returns the 'Are Written As' values for specified list items with natural language between list items preserved.  When only one list item is specified, no in-between language is included.
        """

        if items is None:
            items = xrange(len(self.are_written_as))
        
        self.AWAs = []
        for x in items: 
            if (len(items) > list(items).index(x) + 1):
                ##  NOTE: Here, items references the object's DisplayDuringChoice list; there will never be two identical DisplayDuringChoice items
                ##      otherwise it would be confusing for the user; therefore I can take this shortcut without worrying about .index() returning the first of a set of two identical list items
                self.AWAs.append("{}{}".format(self.are_written_as[x][0], self.are_written_as[x][1]))
            else:
                self.AWAs.append(self.are_written_as[x][0])
        return self.AWAs

    def Get_Permutations(self):
        if self.required_field == True:
            return (2**len(self.are_written_as))-1
        else:
            return 2**len(self.are_written_as)

class Multiple_Randomized_Dynamic_Block(Dynamic_Block):

    """ class Multiple_Randomized_Dynamic_Block(Dynamic_Block): Combines functionality of Multiple_Dynamic_Block and Randomized_Dynamic_Block.
        Example: a = Multiple_Randomized_Dynamic_Block("Display title",[1,2,3],[({1: [33,22,11]}, "in between"),({2: [44,55,66]}, "in between"),({3: [55,66,77]}, "in between")])
    """

    def __init__(self, *args):
        super(Multiple_Randomized_Dynamic_Block, self).__init__(*args)
        self.block_type = "Multiple_Randomized_Dynamic_Block"
        self.alias = "Random Checkbox"

    def Get_AWA(self, items = None):

        """\t Get_AWA(items): Returns the 'Are Written As' values for specified list items, each randomly selected from its corresponding list, with natural language between list items preserved.
        """

        if items is None:
            items = xrange(len(self.are_written_as))
        
        self.AWAs = []
        for x in items:
            if (len(items) > list(items).index(x) + 1):
                self.AWAs.append("{}{}".format(random.choice(self.are_written_as[x][0][self.are_written_as[x][0].keys().pop()]), self.are_written_as[x][1]))
            else:
                self.AWAs.append(random.choice(self.are_written_as[x][0][self.are_written_as[x][0].keys().pop()]))
        return self.AWAs

    def Get_Permutations(self):

        if self.required_field == True:
            one_if_optional = 0
        else:
            one_if_optional = 1

        permutations = 1
        
        for x in xrange(len(self.are_written_as)): 
            permutations_per_box = len(self.are_written_as[x][0].values().pop()) + one_if_optional
            permutations *= permutations_per_box

        return permutations 
        

def Find_DoubleTab_Dividers(split_line):

    """ Find_DoubleTab_Dividers(split_line): Scans through a list and returns the indices wherever two blank values appear next to each other.
    """

    separators = []
            
    for (index, value) in enumerate(split_line):
        if value == "" and split_line[index+1] == "":
            separators.append(index) 

    return separators

def Load_Letter_Blocks(letter_blocks_filename, validation_mode=False):

    """ Load_Letter_Blocks(): Loads all letter blocks from the specified file.
    """

    if validation_mode == False:

        try:
            with open(letter_blocks_filename) as letter_blocks_file:
                letter_blocks = letter_blocks_file.read()
                letter_blocks = letter_blocks.split("\n")
                survey_id = letter_blocks_filename[:-4]
                
        except IOError:
            return (None, None, None)

    else:
        letter_blocks = letter_blocks_filename.split("\n") # letter_blocks_filename in this case is actually the survey passed in directly from the validation form, not an actual file.

    all_letter_blocks = {}
    required_fields = []

    validation = []
    
    for (line_number, line) in enumerate(letter_blocks):

        # Skip blank lines; this will also prevent unnecessary "Unrecognized block: ;" errors when it tries to parse a blank line, most commonly at the end of a file
        if line.strip() == "":
            continue

        split_line= line.strip('\n')
        split_line = split_line.split("\t")        

        # split_line[0] is reserved for the name of the type of letter block
        # split_line[1] is reserved for whether the block is required or not; any value other than "Required", including blanks, denotes optional fields
        # split_line[2] and beyond correspond to the individual letter block's specifications
        

        # split_line[0]: User-friendly aliases for types of letter blocks
        # Static Block:                             Text
        # Randomized Static Block:                  Random Text
        # Dynamic Block:                            Radio
        # Randomized Dynamic Block:                 Random Radio
        # Multiple Dynamic Block:                   Checkbox
        # Multiple Randomized Dynamic Block:        Random Checkbox

        if (split_line[0].replace(" ","_") == "Static_Block" or split_line[0].replace(" ","_") == "Text"):

            try:
                all_letter_blocks[line_number] = Static_Block(split_line[2])
                
            except IndexError, e:
                validation.append("Failed to load {0} at line number {1} for reason {2}; {0} is formatted incorrectly (not enough items).\n".format(split_line[0], line_number, e))
                validation.append("\tHere's the text I stumbled over: {}\n".format(line))
            
        elif (split_line[0].replace(" ","_") == "Randomized_Static_Block" or split_line[0].replace(" ","_") == "Random_Text"):

            try:
                all_letter_blocks[line_number] = Randomized_Static_Block(split_line[2:])
                
            except IndexError, e:
                validation.append("Failed to load {0} at line number {1} for reason {2}; {0} is formatted incorrectly (not enough items).\n".format(split_line[0], line_number, e))
                validation.append("\tHere's the text I stumbled over: {}\n".format(line))
            
        elif (split_line[0].replace(" ","_") == "Dynamic_Block" or split_line[0].replace(" ","_") == "Radio"):

            try:
                ddc = []
                awa = []
                
                for x in xrange(4, len(split_line), 2):

                    ddc.append(split_line[x-1])
                    awa.append(split_line[x])       
                    
                all_letter_blocks[line_number] = Dynamic_Block(split_line[2], ddc, awa)
                
            except IndexError, e:
                validation.append("Failed to load {0} at line number {1} for reason {2}; {0} is formatted incorrectly (not enough items).\n".format(split_line[0], line_number, e))
                validation.append("\tHere's the text I stumbled over: {}\n".format(line))
            
        elif (split_line[0].replace(" ","_") == "Randomized_Dynamic_Block" or split_line[0].replace(" ","_") == "Random_Radio"): 

            try:
                separators = Find_DoubleTab_Dividers(split_line)    
                
                ddc = []
                awa = []
                dict_awa = {}

                for (index, separator) in enumerate(separators): # Separators are going to be in between each set of ddc/awa pairs
                    
                    ddc.append(split_line[separator+2])

                    current_awa = []
                    
                    try:
                        for x in xrange(separator+3, separators[index+1]):
                            current_awa.append(split_line[x])
                        dict_awa[split_line[separator+2]] = current_awa
                    except IndexError:
                        for x in xrange(separator+3, len(split_line)):
                            current_awa.append(split_line[x])
                        dict_awa[split_line[separator+2]] = current_awa

                for single_ddc in ddc:
                    awa.append(({single_ddc: dict_awa[single_ddc]}))

                all_letter_blocks[line_number] = Randomized_Dynamic_Block(split_line[2], ddc, awa)
                
            except IndexError, e:
                validation.append("Failed to load {0} at line number {1} for reason {2}; {0} is formatted incorrectly (not enough items).\n".format(split_line[0], line_number, e))
                validation.append("\tHere's the text I stumbled over: {}\n".format(line))
            
        elif (split_line[0].replace(" ","_") == "Multiple_Dynamic_Block" or split_line[0].replace(" ","_") == "Checkbox"):

            try:
                ddc = []
                awa = []
                inb = []

                for x in xrange(4, len(split_line), 3):
                    ddc.append(split_line[x-1])
                    awa.append(split_line[x])
                    inb.append(split_line[x+1]) 

                write_awa = []
                
                for x in xrange(len(awa)):
                    write_awa.append((awa[x], inb[x]))

                all_letter_blocks[line_number] = Multiple_Dynamic_Block(split_line[2], ddc, write_awa)
                
            except IndexError, e:
                validation.append("Failed to load {0} at line number {1} for reason {2}; {0} is formatted incorrectly (not enough items).\n".format(split_line[0], line_number, e))
                validation.append("\tHere's the text I stumbled over: {}\n".format(line))
            
        elif (split_line[0].replace(" ","_") == "Multiple_Randomized_Dynamic_Block" or split_line[0].replace(" ","_") == "Random_Checkbox"):

            try:
                separators = Find_DoubleTab_Dividers(split_line)

                ddc = []
                awa = []
                inb = []
                dict_awa = {}

                for (index, separator) in enumerate(separators): # Separators are going to be in between each set of ddc/awa/inb trios

                    ddc.append(split_line[separator+2])

                    current_awa = []            

                    try:
                        try:
                            for x in xrange(separator+3, separators[index+1]-1):
                                current_awa.append(split_line[x])
                            inb.append(split_line[x+1])
                            dict_awa[split_line[separator+2]] = current_awa
                        except UnboundLocalError, e:
                            validation.append("Failed to load {0} at line number {1} for reason {2}; {0} is formatted incorrectly (not enough items, or missing tabs).\n".format(split_line[0], line_number, e))
                    except IndexError:
                        try:
                            for x in xrange(separator+3, len(split_line)-1):
                                current_awa.append(split_line[x])
                            inb.append(split_line[x+1])
                            dict_awa[split_line[separator+2]] = current_awa
                        except UnboundLocalError, e:
                            validation.append("Failed to load {0} at line number {1} for reason {2}; {0} is formatted incorrectly (not enough items, or missing tabs).\n".format(split_line[0], line_number, e))

                for (single_ddc, single_inb) in zip(ddc, inb):
                    try:
                        awa.append(({single_ddc: dict_awa[single_ddc]}, single_inb))
                    except KeyError:
                        pass

                all_letter_blocks[line_number] = Multiple_Randomized_Dynamic_Block(split_line[2], ddc, awa)
            except IndexError, e:
                validation.append("Failed to load {0} at line number {1} for reason {2}; {0} is formatted incorrectly (not enough items).\n".format(split_line[0], line_number, e))
                validation.append("\tHere's the text I stumbled over: {}\n".format(line))
            
        else:
            validation.append("Unrecognized type of block: {}; ignoring and moving to the next line".format(split_line[0]))
            continue

        if split_line[1].capitalize() == "Required":
            all_letter_blocks[line_number].SetRequired(True)
            if 'Multiple' in str(all_letter_blocks[line_number].block_type):
                required_fields.append('ck{}'.format(line_number))
            else:
                required_fields.append('rd{}'.format(line_number))

    total_permutations = 1

    for block in all_letter_blocks.itervalues():
        total_permutations *= block.Get_Permutations()

    if validation_mode == True:
        if len(validation) == 0:            
            return (True, Create_EndUser_Survey(0, all_letter_blocks, required_fields), total_permutations)
        else:
            return (False, validation, 0)
    else:
        return (survey_id, all_letter_blocks, required_fields)

def UnformLetter_Generating_JS(required_fields):

    """ UnformLetter_Generating_JS(): Helper function that simply returns a string - the javascript that generates the Unform letter values
            required_fields: Return value of Load_Letter_Blocks()
    """

    required_fields = "', '".join(required_fields)
    required_fields = "['{}']".format(required_fields)

    javascript = """
<script language="JavaScript">
function generate_unform()
{{
    document.forms['cat_herding_laser'].CHL_choices.value = "";
    var elem = document.getElementById('cat_herding_laser').elements;
    var write_this = "";
    for (var i=0;i<elem.length-1;i++)
    {{
        if (elem[i].value != undefined && elem[i].value != '' && elem[i].value != false)
        {{
            if ((elem[i].type == 'radio' && elem[i].checked) || (elem[i].type == 'checkbox' && elem[i].checked) || (elem[i].type != 'radio' && elem[i].type != 'checkbox'))
            {{
                write_this += elem[i].value + " ";
            }}
        }}
    }}
    document.forms['cat_herding_laser'].CHL_choices.value = write_this;// DEBUG ONLY; COMMENT OUT THIS FULL LINE
    
}}
function validate_unform() // Checks that all required fields have been filled out
{{
        var required = {};
        all_required_completed = true; // will get toggled if incomplete

        for (var i=0;i<required.length;i++)
        {{
        	var radio_options = document.getElementsByName(required[i]);
        	var is_checked = false;
        	for (var x=0;x<radio_options.length;x++)
        	{{
			if (document.getElementsByName(required[i])[x].checked)
			{{
				is_checked = true;
			}}
		}}
		if (is_checked == true)
		{{
			document.getElementById('fieldset_' + required[i]).style.background="#ffffff";
		}}
		else
		{{
			all_required_completed = false;
			document.getElementById('fieldset_' + required[i]).style.background="#ff9933";
		}}
	}}
	if (all_required_completed == true)
	{{
		generate_unform();
		document.forms['cat_herding_laser'].submit();
	}}
}}

</script>
""".format(required_fields)

    return javascript

def Create_EndUser_Survey(survey_id, all_letter_blocks, required_fields, form_attributes=None, header=None, footer=None): 
    
    """ Create_EndUser_Survey(all_letter_blocks, header, footer): Creates an HTML form that end-users interact with to generate the un-form letter.
            all_letter_blocks: Return value of Load_Letter_Blocks()
            required_fields: Return value of Load_Letter_Blocks()
            form_attributes: set method, action, and anything else needed here
            header: load in css, branding, heading, or anything else needed here
            footer: footer for the page / pair to the header
    """

    if (survey_id == None and all_letter_blocks == None and required_fields == None):
        return "Survey not found."
    
    source_snippet = []

    if header != None:
        source_snippet.append(header)

    source_snippet.append(UnformLetter_Generating_JS(required_fields))

    if form_attributes == None and survey_id != 0:
        form_attributes = 'method="post" action="submit"'

    source_snippet.append('<form id="cat_herding_laser" name="cat_herding_laser" {}>'.format(form_attributes))
    source_snippet.append('<input type="hidden" name="survey_id" value="{}">'.format(survey_id))

    for x in xrange(len(all_letter_blocks)):
        if 'Static' in all_letter_blocks[x].block_type:
            source_snippet.append('<input type="hidden" name="static{0}" value="{1}">'.format(x, all_letter_blocks[x].Get_AWA().pop().replace('"', "&quot;").rstrip("\n")))
            continue
        if 'Multiple' in str(all_letter_blocks[x].block_type):
            if all_letter_blocks[x].required_field == True:
                source_snippet.append('<fieldset id="fieldset_ck{}"><legend>{} <b>(Required)</b></legend>'.format(x, all_letter_blocks[x].GetTitle()))
            else:
                source_snippet.append('<fieldset id="fieldset_ck{}"><legend>{}</legend>'.format(x, all_letter_blocks[x].GetTitle()))
        else:
            if all_letter_blocks[x].required_field == True:
                source_snippet.append('<fieldset id="fieldset_rd{}"><legend>{} <b>(Required)</b></legend>'.format(x, all_letter_blocks[x].GetTitle()))
            else:
                source_snippet.append('<fieldset id="fieldset_rd{}"><legend>{}</legend>'.format(x, all_letter_blocks[x].GetTitle()))
        for y in xrange(len(all_letter_blocks[x].Get_DDC())):
            if 'Multiple' in str(all_letter_blocks[x].block_type):
                source_snippet.append('<input type="checkbox" name="ck{0}" value="{1}">{2}<br>\n'.format(x, all_letter_blocks[x].Get_AWA([y]).pop().replace('"', "&quot;").rstrip("\n"), all_letter_blocks[x].Get_DDC([y]).pop().replace('"', "&quot;").rstrip("\n")))
            else:
                try: # handles everything except Dynamic_Block
                    source_snippet.append('<input type="radio" name="rd{0}" value="{1}">{2}<br>\n'.format(x, all_letter_blocks[x].Get_AWA([y]).pop().replace('"', "&quot;").rstrip("\n"), all_letter_blocks[x].Get_DDC([y]).pop()))
                except AttributeError: # to handle Dynamic_Block
                    source_snippet.append('<input type="radio" name="rd{0}" value="{1}">{2}<br>\n'.format(x, all_letter_blocks[x].Get_AWA([y]).replace('"', "&quot;").rstrip("\n"), all_letter_blocks[x].Get_DDC([y]).pop()))
                    
        source_snippet.append('</fieldset>\n\n')

    source_snippet.append('<textarea name="CHL_choices" rows=5 cols=30 hidden></textarea>')
    source_snippet.append('<input type="button" name="Submit" onclick=validate_unform() value="Finished!">\n</form>')

    if footer != None:
        source_snippet.append(footer)

    return ''.join(source_snippet)

def Survey_Completed_Page(generated_unform_letter, textarea_attributes='name="cat_herding_laser_ta" rows="14" cols="18"', header=None, form_engine=None, cleanup=None, footer=None):

    """ Output_Blocks(generated_unform_letter, textarea_attributes, header, form_engine, cleanup, footer): Generates the source code for the send-form page that the end-user will see after they've completed the survey.
        This is not called directly; it is called by the submitted form page.
            generated_unform_letter: return value of submitted form
            textarea_attributes: default given; customize html attributes according to need
            header: load in css, branding, heading, or anything else needed here
            form_engine: load in the html needed for the form to work
            cleanup: intended for the form cleanup
            footer: footer for the page / pair to the header
    """

    source_snippet = []

    if header != None:
        source_snippet.append(header)

    if form_engine != None:
        source_snippet.append(form_engine)

    source_snippet.append('<textarea {}>{}</textarea>'.format(textarea_attributes, generated_unform_letter.replace("!!","\n"))) 

    if cleanup != None:
        source_snippet.append(cleanup)

    if footer != None:
        source_snippet.append(footer)

    source_snippet.append('</body></html>')
    
    return ''.join(source_snippet)

class Root(object):

    """ CherryPy Root class for serving the survey page. """

    def __init__(self):
        pass

    def admin(self):

        """ cherrypy.Root.admin(): This is where the admin goes to create the survey. """

        admin_filename = "admin.txt"

        with open(admin_filename) as admin_file:
            admin_source = admin_file.read()
        
        return admin_source

    def createsurvey(self, **kwargs):

        """ cherrypy.Root.createsurvey(): Action of cherrypy.Root.admin(); survey_id is displayed here. """

        if kwargs.get('survey', "") != "":
            survey_id = hashlib.new('md5', kwargs['survey']).hexdigest()
            with open("{}.txt".format(survey_id), "w") as write_survey_file:
                write_survey_file.write(kwargs['survey'])
        else:
            return "Can't create a blank survey!"

        # Just to get the Total Permutations - I think this is a cool stat to display for those creating the survey
        (survey_validation, returned_source, total_permutations) = Load_Letter_Blocks(kwargs['survey'], validation_mode=True)

        kwargs.pop('survey')

        for (key, value) in kwargs.iteritems():
            if value != "":
                with open("{}_{}.txt".format(survey_id, key), "w") as write_file:
                    write_file.write(value)
        
        return "<a href='../survey?survey_id={0}'>Survey #{0}</a> created successfully.<br>&nbsp;<br>Based on your supporters' choices, this could create as many as <b>{1:,}</b> unique Un-form letters.  Mathematical!".format(survey_id, total_permutations)

    def index(self):

        """ cherrypy.Root.index(): Without this, a 404 error would occur at the root.  Customize as desired. """
        
        return # Returns nothing; change as needed

    def survey(self, survey_id=None):

        """ cherrypy.Root.survey(): The survey page to send supporters to.  Access through /survey?survey_id=<md5 hash> """

        if survey_id == None:
            return # Returns nothing; change as needed

        keys = ['survey_header', 'survey_footer']

        options = {}.fromkeys(keys, "")

        for key in keys:
            try:
                with open("{}_{}.txt".format(survey_id, key)) as options_file:
                    options[key] = options_file.read()
            except IOError:
                pass
            
        (survey_id, all_letter_blocks, required_fields) = Load_Letter_Blocks("{}.txt".format(survey_id))
        return Create_EndUser_Survey(survey_id, all_letter_blocks, required_fields, header=options['survey_header'], footer=options['survey_footer'])
        
    def submit(self, **kwargs):

        """ cherrypy.Root.submit(): Action of cherrypy.Root.survey(); Contains the unform letter generated by the user's survey choices. """

        try:   
            self.survey_id = kwargs['survey_id']
        except KeyError:
            return # Returns nothing so you can't go directly to /submit; change as needed

        # Saves the response; keys are sorted (ck, rd, static; CHL_choices, survey_id)
        response = []
        sorted_response_keys = kwargs.keys()
        sorted_response_keys.sort()
        
        with open("{}-responses.txt".format(self.survey_id), "a") as responses_file:
            for key in sorted_response_keys:
                response.append("{}: {}".format(key, kwargs[key]))
            for (index, value) in enumerate(response):
                response[index] = value.replace("\t", "").replace("\n", "").replace("\r", "")
            response = "{}\n".format('\t'.join(response))         
            responses_file.write(response)

        keys = ['completed_textarea', 'completed_header', 'completed_engine', 'completed_cleanup', 'completed_footer']

        options = {}.fromkeys(keys, "")

        for key in keys:
            try:
                with open("{}_{}.txt".format(self.survey_id, key)) as options_file:
                    options[key] = options_file.read()
            except IOError:
                pass
            
        return Survey_Completed_Page(kwargs['CHL_choices'], textarea_attributes=options['completed_textarea'], header=options['completed_header'], form_engine=options['completed_engine'], cleanup=options['completed_cleanup'], footer=options['completed_footer']).replace(self.survey_id, '')

    def validate(self, **kwargs):

        """ cherrypy.Root.submit(): Useful for admins to validate their survey and receive helpful error messages if they made a syntax error in assembling it. """

        if kwargs.get('survey', "") != "":

            (survey_validation, returned_source, total_permutations) = Load_Letter_Blocks(kwargs['survey'], validation_mode=True)
            if survey_validation == True: # Survey passed; preview the survey
                return "Your survey passed validation! Below is a preview.  When you're ready to create your survey, go to <a href='../admin'>Create Survey</a>.<br>&nbsp;<br>Based on your supporters' choices, this could create as many as <b>{:,}</b> unique Un-form letters.  Mathematical!<br>&nbsp; <br>{}".format(total_permutations, returned_source.replace("document.forms['cat_herding_laser'].submit();", "").replace('<textarea name="CHL_choices" rows=5 cols=30 hidden>', '<textarea name="CHL_choices" rows=5 cols=30>'))
            else:            
                return "Your survey had some errors in it, here's a summary: <br>{}".format('<br>\n'.join(returned_source))
        else:
            return "<html><form method=post action=validate>Copy and paste your survey below:<br><textarea name=survey cols=30 rows=15></textarea><input type=submit value='Validate Survey'></form></html>"

    admin.exposed = True
    createsurvey.exposed = True
    index.exposed = True
    survey.exposed = True
    submit.exposed = True
    validate.exposed = True


if __name__ == "__main__":

    configuration_file = 'cfg.cfg'

    cherrypy.root = Root()
    cherrypy.config.update(configuration_file)
    cherrypy.quickstart(cherrypy.root)        
