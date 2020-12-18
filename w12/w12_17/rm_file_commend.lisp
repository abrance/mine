(defun rm_file_commend
  (f_path)
  (let ((file_stram (open (f_path :direction output)))
	(let ((new_path (concat f_path "-new"))

	      (setq new_file (open (new_path :direction input :if-exists nil)))

	      (dolist (str (read-line file_stram))
		(if (include str "//")
		    (setq '(keep rm-part) (split "//" str))
		    (replace i _i)
		    ))
	      ))
	))
  )

