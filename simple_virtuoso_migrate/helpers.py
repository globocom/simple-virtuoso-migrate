import os
import sys
import tempfile
import codecs


class Utils(object):

    @staticmethod
    def write_temporary_file(content, content_reference):
        try:
            f = tempfile.NamedTemporaryFile(delete=False)
            f.close()

            fh = codecs.open(f.name, 'w', encoding='utf-8')
            fh.write(content)
            fh.close()
            return f.name
        except IOError, e:
            raise Exception("could not create temporary file for %s -> (%s)" %
                                                        (content_reference, e))

    @staticmethod
    def get_variables_from_file(full_filename, file_encoding='utf-8'):
        path, filename = os.path.split(full_filename)
        temp_abspath = None

        global_dict = globals().copy()
        local_dict = {}

        try:
            # add settings dir from path
            sys.path.insert(0, path)

            execfile(full_filename, global_dict, local_dict)
        except IOError:
            raise Exception("%s: file not found" % full_filename)
        except Exception, e:
            try:
                f = open(full_filename, "rU")
                content = f.read()
                f.close()

                temp_abspath = "%s/%s" % (tempfile.gettempdir().rstrip('/'),
                                          filename)
                f = open(temp_abspath, "w")
                f.write('#-*- coding:%s -*-\n%s' % (file_encoding, content))
                f.close()

                execfile(temp_abspath, global_dict, local_dict)
            except Exception, e:
                raise Exception("error interpreting config file '%s': %s" %
                                                            (filename, str(e)))
        finally:
            #erase temp and compiled files
            if temp_abspath and os.path.isfile(temp_abspath):
                os.remove(temp_abspath)

            # remove settings dir from path
            if path in sys.path:
                sys.path.remove(path)

        return local_dict
