#ifndef __PARSER_CONTEXT_H
#define __PARSER_CONTEXT_H

#include "File.h"

class ParserContext {
private:
	int    get_options(int argc, char *argv[], const char *short_options, const struct option *long_options);
	int    last_optind;
	int    levels;
	int    do_quote;
	void   Reset();

public:
	enum OF_TYPE { OF_NULL = 0, OF_STDOUT, OF_NORM };
	static const char MAGIC_CHAR;
	CC_ARRAY<CC_STRING>  source_files;

	CC_ARRAY<CC_STRING>  i_dirs;
	CC_ARRAY<CC_STRING>  isystem_dirs;
	CC_ARRAY<CC_STRING>  after_dirs;
	CC_ARRAY<CC_STRING>  compiler_dirs;

	MemFile             predef_macros;
//	CC_STRING            outfile;

	/* Additional output files */
	CC_STRING            of_dep; /* dependencies */
	CC_STRING            of_cl;  /* command line */
	CC_STRING            of_con; /* conditional evaluation */

	CC_STRING            baksuffix;
	CC_STRING            cc;
	CC_STRING            cc_path;
	CC_STRING            cc_args;
	CC_STRING            my_args;
	CC_ARRAY<CC_STRING>  imacro_files;
	CC_STRING            topdir;

	CC_ARRAY<CC_STRING>  include_files;
	CC_ARRAY<CC_STRING>  ignore_list;
	bool                 no_stdinc;
	bool                 print_help;
	char                 as_lc_char;  // Assembler line command char
	OF_TYPE              outfile;

	CC_STRING            errmsg;
	int                  argc;
	char               **argv;

	int    get_options(int argc, char *argv[]);
	void   save_cc_args();
	void   save_my_args();

	bool check_ignore(const CC_STRING& filename);
	CC_STRING get_include_file_path(const CC_STRING& included_file, const CC_STRING& current_file,
		bool quote_include, bool include_next, bool *in_sys_dir);
	ParserContext();
};

#endif
